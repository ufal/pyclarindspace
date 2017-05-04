# coding=utf-8
import logging
from pprint import pformat
from ._collection import collection
_logger = logging.getLogger("clarindspace")


class community(object):
    """
        DSpace community representation. Holds name & id; methods to handle collections
    """

    def __init__(self, name, com_id, repository=None):
        self._name = name
        self._id = com_id
        self._repository = repository

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    def create_collection(self, name):
        """
            Create collection in this community with given name, no check for preexisting
        """
        js = self._repository.api_post(
            '/communities/' + str(self._id) + '/collections', {'name': name})
        logging.info(
            'Created collection with name [%s] and id [%s]', name, js['id'])
        return collection(name, js['id'], self._repository)

    def find_collection_by_name(self, name):
        js = self._repository.api_get(
            '/communities/' + str(self._id) + '/collections')
        collections = {col['name']: col['id'] for col in js}
        logging.debug(pformat(collections))
        if name not in collections:
            logging.info('Collection [%s] not found', name)
            return None
        return collection(name, collections[name], self._repository)

    def find_or_create_collection(self, name):
        """
            Search for collection by name and if fail create new one with that name
        """
        col = self.find_collection_by_name(name)
        return col if col is not None else self.create_collection(name)
