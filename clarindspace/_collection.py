# coding=utf-8
import logging
from ._item import item


class collection(object):
    """
        DSpace collection representation. Holds name & id; methods to handle items
    """

    def __init__(self, name, col_id, repository=None):
        """Constructor for Collection"""
        self._name = name
        self._id = col_id
        self._repository = repository

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    def create_item(self, item_metadata):
        """Create item in this collection"""
        url = '/collections/' + str(self._id) + '/items'
        js = self._repository.api_post(url, {'metadata': item_metadata})
        logging.info(
            'Created item with name [%s] and id [%s] and handle [%s]',
            js['name'],
            js['id'],
            js['handle']
        )
        return item(js['name'], js['id'], js['handle'], self._repository)

    def get_items(self):
        """Fetch all items in collection"""
        # No paging list all hack
        url = '/collections/' + str(self._id) + '?expand=items&limit=-1'
        js = self._repository.api_get(url)
        logging.info('Fetched items for collection [%s]', self._name)
        return (item(js_item['name'], js_item['id'], js_item['handle']) for js_item in js['items'])

