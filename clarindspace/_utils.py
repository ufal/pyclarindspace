# coding=utf-8
import json
try:
    from urllib import urlopen, urlretrieve
    from urlparse import urljoin
except:
    from urllib.request import urlopen, urlretrieve
    from urllib.parse import urljoin


def json_from_url(url, encoding="utf-8"):
    """
        python2/3 json load from url
    """
    js_str = urlopen(url).read().decode(encoding)
    return json.loads(js_str)
