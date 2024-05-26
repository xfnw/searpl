#!/usr/bin/env python3

import argparse, sqlite3
from time import sleep
from urllib import request, robotparser
from urllib.error import HTTPError
from urllib.parse import urlparse
from lxml.html import fromstring

ua = "searplbot/2.0"
headers = {"User-Agent": ua}


class RobotCache:
    """shim to make urllib.robotparser.RobotFileParser work with multiple domains"""

    def __init__(self, delay=1):
        self.cache = {}
        self.delay = delay

    def download(self, url):
        robot = robotparser.RobotFileParser()
        robot.set_url(url._replace(path="/robots.txt", fragment="").geturl())

        try:
            robot.parse(get(robot.url).read().decode("utf-8").splitlines())
        except HTTPError as e:
            if e.code in (401, 403):
                robot.disallow_all = True
            else:
                robot.allow_all = True
        except:
            robot.disallow_all = True

        self.cache[url.netloc] = robot

    def can_fetch(self, url):
        purl = urlparse(url)
        domain = purl.netloc

        if domain not in self.cache:
            self.download(purl)

        rb = self.cache[domain]

        # just skip pages that ask for a higher delay than
        # we are using; no point in waiting around when we
        # have other sites to crawl
        if (rb.crawl_delay(ua) or 0) > self.delay:
            return False

        return rb.can_fetch(ua, url)


def get(url, timeout=2):
    req = request.Request(url, headers=headers, unverifiable=True)
    return request.urlopen(req, timeout=timeout)


def pop_url(db):
    db.execute("DELETE FROM tocrawl WHERE url IN (SELECT url FROM indexed)")

    db.execute(
        "DELETE FROM tocrawl WHERE rowid IN (SELECT rowid FROM tocrawl ORDER BY RANDOM() LIMIT 1) RETURNING url"
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
        html = fromstring(res.read())
        html.make_links_absolute(url)
    except Exception as e:
        print("oh no", e)
        return

    for element in html.cssselect("a"):
        newurl = urlparse(element.attrib.get("href"))._replace(fragment="")

        if newurl.scheme not in ("https", "http"):
            continue

        newurl = newurl.geturl()

        db.execute(
            "INSERT INTO tocrawl (url) VALUES (?) ON CONFLICT DO NOTHING", (newurl,)
        )

    titles = html.cssselect("title")
    if len(titles) == 0:
        return
    title = titles[0].text_content()

    # FIXME: clean up pages better, perhaps using readability
    for element in html.cssselect("script, style"):
        element.drop_tree()

    print("title:", title)
    db.execute("DELETE FROM indexed WHERE url = ?", (url,))
    db.execute(
        "INSERT INTO indexed (title, url, content) VALUES (?, ?, ?)",
        (title, url, html.text_content()),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", help="crawl count", default=0, type=int)
    parser.add_argument("-d", help="crawl delay", default=1, type=float)
    parser.add_argument("database")
    parser.add_argument("url", nargs="*")
    args = parser.parse_args()

    con = sqlite3.connect(args.database)
    cur = con.cursor()

    robots = RobotCache(delay=args.d)

    for url in args.url:
        print("indexing", url)
        index_page(url, cur, robots)
        con.commit()
        sleep(args.d)

    for i in range(args.c):
        url = pop_url(cur)
        con.commit()
        print("indexing", url)
        index_page(url, cur, robots)
        con.commit()
        sleep(args.d)


if __name__ == "__main__":
    main()
