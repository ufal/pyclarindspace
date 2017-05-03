import requests
import logging
from pprint import pformat
from clarin_dspace.content.Item import Item


class Collection(object):
    """DSpace collection representation. Holds name & id; methods to handle items"""

    def __init__(self, name, col_id, parent=None):
        """Constructor for Collection"""
        self.name = name
        self.id = col_id
        self.parent = parent

    def create_item(self, item_metadata):
        """Create item in this collection"""
        url = self.get_api_url() + '/collections/' + str(self.id) + '/items'
        r = requests.post(url, json={'metadata': item_metadata}, headers=self.get_request_headers())
        logging.debug(pformat(r))
        r.raise_for_status()
        item = r.json()
        logging.info('Created item with name "{}" and id "{}"'.format(item['name'],
                                                                      item['id']))
        return Item(item['name'], item['id'], item['handle'], self)

    def get_request_headers(self):
        return self.parent.get_request_headers()

    def get_api_url(self):
        return self.parent.get_api_url()
