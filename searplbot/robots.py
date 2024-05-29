from urllib.robotparser import RobotFileParser
from urllib.error import HTTPError
from urllib.parse import urlparse

from .agent import get


class RobotCache:
    """shim to make RobotFileParser work with multiple domains"""

    from .searplbot import get

    def __init__(self, ua, delay=1):
        self.cache = {}
        self.delay = delay
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

    def can_fetch(self, url):
        purl = urlparse(url)
        domain = purl.netloc

        if domain not in self.cache:
            self.download(purl)

        rb = self.cache[domain]

        # just skip pages that ask for a higher delay than
        # we are using; no point in waiting around when we
        # have other sites to crawl
        if (rb.crawl_delay(self.ua) or 0) > self.delay:
            return False

        return rb.can_fetch(self.ua, url)
