from urllib import request

ua = "searplbot/2.0"
headers = {"User-Agent": ua}


def get(url, timeout=2):
    req = request.Request(url, headers=headers, unverifiable=True)
    return request.urlopen(req, timeout=timeout)
