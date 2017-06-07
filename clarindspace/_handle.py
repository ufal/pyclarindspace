# coding=utf-8
import logging
import json
from ._utils import urlopen, json_from_url
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
            js = json_from_url(handle.api_url + self.basename())
            js = js["values"]
            return js
