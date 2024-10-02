#!/usr/bin/env python3

import argparse, sqlite3
from time import sleep
from urllib.parse import urlparse
from lxml.html import HTMLParser, fromstring
from lxml.etree import iterwalk

from .agent import get, ua
from .robots import RobotCache
from .replace import MultiReplace

esc = MultiReplace({"<": "&lt;", ">": "&gt;", "'": "&apos;", '"': "&quot;"}).replace


def pop_url(db):
    db.execute(
        "DELETE FROM tocrawl WHERE url IN (SELECT url FROM indexed WHERE content != '')"
    )

    db.execute(
        """DELETE FROM tocrawl WHERE rowid IN
        (SELECT rowid FROM tocrawl WHERE netloc =
        (SELECT netloc FROM tocrawl GROUP BY netloc ORDER BY RANDOM() LIMIT 1)
        ORDER BY RANDOM() LIMIT 1)
        RETURNING url"""
    )

    if res := db.fetchone():
        url = res[0]
        db.execute("DELETE FROM indexed WHERE url = ?", (url,))
        return url

    raise Exception("no more urls")


def squish_text(inp):
    res = []
    for ev, e in iterwalk(inp, events=("start", "end")):
        if ev == "start" and e.text and (s := e.text.strip()):
            res.append(s)
        elif ev == "end" and e.tail and (s := e.tail.strip()):
            res.append(s)
    return " ".join(res)


def index_page(url, db, robots):
    if not robots.can_fetch(url):
        print("beep boop")
        return

    try:
        res = get(url)
        if (
            res.headers.get_content_maintype() != "text"
            and res.headers.get_content_type() != "application/xhtml+xml"
        ):
            return
        url = res.url  # follow redirects
        parser = HTMLParser(remove_blank_text=True, encoding="utf-8")
        html = fromstring(res.read(2097152), parser=parser)
        html.text_content()
        html.make_links_absolute(url)
    except Exception as e:
        print("oh no", e)
        return

    # FIXME: should probably be case-insensitive?
    if html.xpath(
        "//meta[(@name = 'robots' or @name = 'searplbot') and (contains(@content, 'noindex') or contains(@content, 'nofollow'))]"
    ):
        print("boop beep")
        return

    url = urlparse(url)
    if url.path == "/":
        url = url._replace(path="")
    url = url._replace(fragment="").geturl()

    # FIXME: clean up pages better, perhaps using readability
    for element in html.cssselect("script, style, noindex"):
        element.drop_tree()

    for element in html.xpath("//a[not(@rel and contains(@rel, 'nofollow'))]"):
        newurl = urlparse(element.attrib.get("href"))._replace(fragment="")

        if newurl.scheme not in ("https", "http"):
            continue
        if newurl.path == "/":
            newurl = newurl._replace(path="")

        netloc = newurl.netloc
        newurl = newurl.geturl()

        db.execute(
            "INSERT INTO tocrawl (url, netloc) VALUES (?, ?) ON CONFLICT DO NOTHING",
            (newurl, netloc),
        )

    titles = html.cssselect("title")
    if len(titles) == 0:
        return
    title = squish_text(titles[0])
    if not title:
        return
    content = squish_text(html)

    print("title:", title)
    db.execute("DELETE FROM indexed WHERE url = ?", (url,))
    db.execute(
        "INSERT INTO indexed (title, url, content) VALUES (?, ?, ?)",
        (esc(title), esc(url), esc(content)),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", help="crawl count", default=0, type=int)
    parser.add_argument("-d", help="crawl delay", default=1, type=float)
    parser.add_argument("-f", help="use urls from file")
    parser.add_argument("-R", help="purge tocrawl list", action="store_true")
    parser.add_argument("database")
    parser.add_argument("url", nargs="*")
    args = parser.parse_args()

    con = sqlite3.connect(args.database)
    cur = con.cursor()

    if args.R:
        cur.execute("DELETE FROM tocrawl")

    if args.f:
        with open(args.f, "r") as f:
            args.url += f.read().splitlines()

    robots = RobotCache(ua)

    for url in args.url:
        cur.execute("DELETE FROM indexed WHERE url = ?", (url,))
        con.commit()
        print("indexing", url)
        index_page(url, cur, robots)
        con.commit()
        sleep(args.d)

    for _ in range(args.c):
        url = pop_url(cur)
        con.commit()
        print("indexing", url)
        index_page(url, cur, robots)
        con.commit()
        sleep(args.d)


if __name__ == "__main__":
    main()
