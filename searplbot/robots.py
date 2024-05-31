from urllib.robotparser import RobotFileParser
from urllib.error import HTTPError
from urllib.parse import urlparse
from time import time

from .agent import get


class RobotCache:
    """shim to make RobotFileParser work with multiple domains"""

    from .searplbot import get

    def __init__(self, ua):
        self.cache = {}
        self.last = {}
        self.ua = ua

    def download(self, url):
        robot = RobotFileParser()
        robot.set_url(
            url._replace(path="/robots.txt", params="", query="", fragment="").geturl()
        )

        try:
            robot.parse(get(robot.url).read().decode("utf-8").splitlines())
        except HTTPError as e:
            if e.code in (401, 403):
                robot.disallow_all = True
            else:
                robot.allow_all = True
        except Exception:
            robot.disallow_all = True

        self.cache[url.netloc] = robot
        self.last[url.netloc] = 0

    def can_fetch(self, url):
        purl = urlparse(url)
        domain = purl.netloc

        if domain not in self.cache:
            self.download(purl)

        rb = self.cache[domain]

        now = time()
        if (rb.crawl_delay(self.ua) or 0) + self.last[domain] > now:
            return False
        self.last[domain] = now

        return rb.can_fetch(self.ua, url)
