#!/usr/bin/env python3

import argparse, sqlite3
from urllib import request, parse as urlparse
from lxml.html import fromstring

ua = "searplbot/2.0"
headers = {"User-Agent": ua}


def get(url, timeout=2):
    req = request.Request(url, headers=headers, unverifiable=True)
    return request.urlopen(req, timeout=timeout)


def pop_url(db):
    db.execute('DELETE FROM tocrawl WHERE rowid IN (SELECT rowid FROM tocrawl ORDER BY RANDOM() LIMIT 1) RETURNING url')

    if res := db.fetchone():
        print(res)
        return

    raise Exception("no more urls")


def index_page(url, db):
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("database")
    parser.add_argument("url", nargs="*")
    args = parser.parse_args()

    con = sqlite3.connect(args.database)
    cur = con.cursor()

    urls = args.url
    if len(urls) == 0:
        urls.append(pop_url(cur))

    for url in urls:
        print("indexing", url)
        index_page(url, cur)


if __name__ == "__main__":
    main()
