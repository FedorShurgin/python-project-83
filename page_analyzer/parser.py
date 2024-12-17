from urllib.parse import urlparse


def parse(url):
    url_parse = urlparse(url)
    return f"{url_parse.scheme}://{url_parse.hostname}"
