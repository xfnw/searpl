from urllib import request

ua = "searplbot/2.0"
headers = {"User-Agent": ua}


def get(url, timeout=2, robots=None):
    if robots and not robots.can_fetch(url):
        return

    req = request.Request(url, headers=headers, unverifiable=True)
    return request.urlopen(req, timeout=timeout)
