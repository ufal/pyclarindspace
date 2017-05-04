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
        logging.info('Created item with name [%s] and id [%s]', js[
                     'name'], js['id'])
        return item(js['name'], js['id'], js['handle'], self._repository)
