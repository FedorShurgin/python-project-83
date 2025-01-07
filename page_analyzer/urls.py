from urllib.parse import urlparse
import validators


def parse(url):
    url_parse = urlparse(url)
    return f"{url_parse.scheme}://{url_parse.hostname}"


def validate_url(url):
    if len(url) > 255:
        return 'URL превышает 255 символов'
    if not validators.url(url):
        return 'Некорректный URL'
