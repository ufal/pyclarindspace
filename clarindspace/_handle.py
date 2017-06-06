# coding=utf-8
try:
    from urllib import urlopen
except:
    from urllib.request import urlopen
import logging
import json
_logger = logging.getLogger("clarindspace")


class handle(object):
    """
        Show handle information.        
    """
    api_url = "http://hdl.handle.net/api/handles/"

    def __init__(self, handle_url):
        self._hurl = handle_url

    def basename(self):
        return "/".join(self._hurl.split("/")[-2:])

    def handle_metadata(self, new_interface=False):
        if not new_interface:
            metadata = urlopen(self._hurl + "?noredirect").read()
            return metadata
        else:
            js_str = urlopen(handle.api_url + self.basename()).read()
            js = json.loads(js_str)
            js = js["values"]
            return js
