#!/usr/bin/env python3

import argparse, sqlite3
from time import sleep
from urllib.parse import urlparse
from lxml.html import HTMLParser, fromstring

from .agent import get, ua
from .robots import RobotCache
from .replace import MultiReplace

esc = MultiReplace({"<": "&lt;", ">": "&gt;", "'": "&apos;", '"': "&quot;"}).replace


def pop_url(db):
    db.execute("DELETE FROM tocrawl WHERE url IN (SELECT url FROM indexed)")

    db.execute(
        """DELETE FROM tocrawl WHERE rowid IN
        (SELECT rowid FROM tocrawl WHERE netloc =
        (SELECT netloc FROM tocrawl GROUP BY netloc ORDER BY RANDOM() LIMIT 1)
        ORDER BY RANDOM() LIMIT 1)
        RETURNING url"""
    )

    if res := db.fetchone():
        return res[0]

    raise Exception("no more urls")


def index_page(url, db, robots):
    if not robots.can_fetch(url):
        print("beep boop")
        return

    try:
        res = get(url)
        if not res.headers.get_content_maintype() == "text":
            return
        url = res.url  # follow redirects
        parser = HTMLParser(remove_blank_text=True)
        html = fromstring(res.read(), parser=parser)
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

    # FIXME: clean up pages better, perhaps using readability
    for element in html.cssselect("script, style, noindex"):
        element.drop_tree()

    for element in html.xpath("//a[not(@rel and contains(@rel, 'nofollow'))]"):
        newurl = urlparse(element.attrib.get("href"))._replace(fragment="")

        if newurl.scheme not in ("https", "http"):
            continue

        netloc = newurl.netloc
        newurl = newurl.geturl()

        db.execute(
            "INSERT INTO tocrawl (url, netloc) VALUES (?, ?) ON CONFLICT DO NOTHING",
            (newurl, netloc),
        )

    titles = html.cssselect("title")
    if len(titles) == 0:
        return

    try:
        title = titles[0].text_content()
        content = html.text_content()
    except UnicodeDecodeError:
        print("ut oh")
        return

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
    parser.add_argument("-R", help="purge tocrawl list", action="store_true")
    parser.add_argument("database")
    parser.add_argument("url", nargs="*")
    args = parser.parse_args()

    con = sqlite3.connect(args.database)
    cur = con.cursor()

    if args.R:
        cur.execute("DELETE FROM tocrawl")

    robots = RobotCache(ua, delay=args.d)

    for url in args.url:
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
