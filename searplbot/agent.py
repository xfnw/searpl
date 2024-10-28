from urllib import request, error

ua = "searplbot/2.0"
headers = {"User-Agent": ua}


class HTTPRedirectHandler(request.HTTPRedirectHandler):
    robots = None

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)

        if self.robots and new and not self.robots.can_fetch(new.get_full_url()):
            raise error.HTTPError(newurl, code, "redirected to beep boop", headers, fp)

        return new


def get(url, timeout=2, robots=None):
    if robots and not robots.can_fetch(url):
        return

    hand = HTTPRedirectHandler()
    hand.robots = robots

    opener = request.build_opener(hand)

    req = request.Request(url, headers=headers, unverifiable=True)
    return opener.open(req, timeout=timeout)
