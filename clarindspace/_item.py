# coding=utf-8
import os
import logging
from requests_toolbelt.multipart.encoder import MultipartEncoder
from pprint import pformat


class item(object):
    """
        DSpace item representation. Holds name, id & handle; methods to add bitstreams
    """

    def __init__(self, name, item_id, handle, repository=None):
        """Constructor for Item"""
        self._name = name
        self._id = item_id
        self._handle = handle
        self._repository = repository

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def handle(self):
        return self._handle

    def add_bitstream(self, data_file_path):
        """
            Upload file located at data_file_path to item
        """
        # get file name; used as the bitstream name & for format detection
        data_file_name = os.path.basename(data_file_path)
        url = '/items/' + str(self._id) + '/bitstreams?name=' + data_file_name

        # With this encoder the file should not be read in memory, but streamed
        # right away
        m = MultipartEncoder([('filename', open(data_file_path, 'rb'))])

        js = self._repository.api_post(
            url, json_data=None, headers_update={'Content-Type': m.content_type}, data=m
        )
        logging.info(
            'Created bitstream with name [%s] and id [%s]\n%s',
            data_file_name, js['id'], pformat(js)
        )

    def replace_metadata_field(self, json_metadata_entry_array):
        """
            MetadataEntry is {key, value, lang} object. PUT clears all the values mapped to the
            key in item and adds those from the MetadataEntry.
        """
        self._repository.api_put(
            '/items/' + str(self._id) + '/metadata', json_metadata_entry_array)
        logging.info('Successfully replaced metadata on item [%s].', self._id)

    def update_identifier(self, handle):
        """
            Replace all dc.identifier.uri with the supplied handle
        """
        self.replace_metadata_field(
            [{
                'key': 'dc.identifier.uri',
                'value': handle,
                'language': None
            }]
        )
