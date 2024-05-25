#!/usr/bin/env python3

import argparse, sqlite3
from urllib import request, robotparser
from urllib.parse import urlparse
from lxml.html import fromstring

ua = "searplbot/2.0"
headers = {"User-Agent": ua}


def get(url, timeout=2):
    req = request.Request(url, headers=headers, unverifiable=True)
    return request.urlopen(req, timeout=timeout)


def pop_url(db):
    db.execute(
        "DELETE FROM tocrawl WHERE rowid IN (SELECT rowid FROM tocrawl ORDER BY RANDOM() LIMIT 1) RETURNING url"
    )

    if res := db.fetchone():
        return res[0]

    raise Exception("no more urls")


def index_page(url, db):
    # TODO: check robots.txt here

    try:
        res = get(url)
        if not res.headers.get_content_maintype() == "text":
            return
        html = fromstring(res.read())
        html.make_links_absolute(url)
    except Exception as e:
        print("oh no", e)
        return

    for element in html.cssselect("a"):
        newurl = urlparse(element.attrib.get("href"))._replace(fragment="").geturl()
        db.execute(
            "INSERT INTO tocrawl (url) VALUES (?) ON CONFLICT DO NOTHING", (newurl,)
        )

    titles = html.cssselect("title")
    if len(titles) == 0:
        return
    title = titles[0].text_content()
    print("title:", title)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", help="crawl count", default=0)
    parser.add_argument("database")
    parser.add_argument("url", nargs="*")
    args = parser.parse_args()

    con = sqlite3.connect(args.database)
    cur = con.cursor()

    for url in args.url:
        print("indexing", url)
        index_page(url, cur)
        con.commit()

    for i in range(int(args.c)):
        url = pop_url(cur)
        con.commit()
        print("indexing", url)
        index_page(url, cur)
        con.commit()


if __name__ == "__main__":
    main()
