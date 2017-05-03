import requests
import logging
from pprint import pformat
from clarin_dspace.content.Collection import Collection


class Community(object):
    """DSpace community representation. Holds name & id; methods to handle collections"""

    def __init__(self, name, com_id, parent=None):
        """Constructor for Community"""
        self.name = name
        self.id = com_id
        self.parent = parent

    def create_collection(self, collection_name):
        """Create collection in this community with given name, no check for preexisting"""
        url = self.get_api_url() + '/communities/' + str(self.id) + '/collections'
        r = requests.post(url, json={'name': collection_name}, headers=self.get_request_headers())
        logging.debug(pformat(r))
        r.raise_for_status()
        collection = r.json()
        logging.info('Created collection with name "{}" and id "{}"'.format(collection_name,
                                                                            collection['id']))
        return Collection(collection_name, collection['id'], self)

    def find_collection_by_name(self, collection_name):
        url = self.get_api_url() + '/communities/' + str(self.id) + '/collections'
        r = requests.get(url, headers=self.get_request_headers())
        logging.debug(pformat(r))
        r.raise_for_status()
        collections = {collection['name']: collection['id'] for (collection) in r.json()}
        logging.debug(pformat(collections))
        if collection_name in collections:
            return Collection(collection_name, collections[collection_name], self)
        else:
            logging.info('Collection "{}" not found'.format(collection_name))

    def find_or_create_collection(self, collection_name):
        """Search for collection by name and if fail create new one with that name"""
        collection = self.find_collection_by_name(collection_name)
        return collection if collection else self.create_collection(collection_name)

    def get_request_headers(self):
        return self.parent.get_request_headers()

    def get_api_url(self):
        return self.parent.get_api_url()
