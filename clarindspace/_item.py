# coding=utf-8
import os
import logging
from ._utils import urlopen
from pprint import pformat
from requests_toolbelt.multipart.encoder import MultipartEncoder
_logger = logging.getLogger("clarindspace")


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

    @staticmethod
    def bitstream_info_from_pid(pid_url, mimetype=None):
        """
            Appends well known magic to the `pid_url` and retrieves the  metadata instead of the 
            landing page. The metadata are parsed to get the mimetype and bitstream url.

            The algorithm looks for items that have ResourceType set to `Resource`.
        """
        import xml.etree.ElementTree as ET
        pid_metadata_url = pid_url + "@format=cmdi"

        _logger.info("Fetching metadata in CMDI format [%s]", pid_metadata_url)
        ns = "{http://www.clarin.eu/cmd/}"
        metadata = urlopen(pid_metadata_url).read()
        root = ET.fromstring(metadata)

        # finding bitstream elements
        bitstream_info_arr = []
        for proxy in root.findall('.//%sResourceProxy' % ns):
            rt = proxy.find("./%sResourceType" % ns)
            rr = proxy.find("./%sResourceRef" % ns)
            if rt.text == "Resource":
                bitstream_info_arr.append(
                    (rt.attrib.get("mimetype", "unknown"), rr.text)
                )
        _logger.info("Found [%d] bitstreams elements in ResourceProxy elements", len(
            bitstream_info_arr))

        if mimetype is not None:
            _logger.info(
                "Filtering bitstreams according to specified mimetype [%s]", mimetype)
            bitstream_info_arr = [
                x for x in bitstream_info_arr if x[0] == mimetype]

        _logger.info(
            "Found\n%s",
            "\n".join(["%2d. %s [%s]" % (i, x[1], x[0])
                       for i, x in enumerate(bitstream_info_arr)])
        )
        return bitstream_info_arr

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def handle(self):
        return self._handle

    def add_bitstream(self, data_file_path, mime_type=None):
        """
            Upload file located at data_file_path to item
        """
        # get file name; used as the bitstream name & for format detection
        data_file_name = os.path.basename(data_file_path)
        url = '/items/' + str(self._id) + '/bitstreams?name=' + data_file_name
        if mime_type is not None:
            url += "&file_mime_type=%s" % mime_type

        js = self._repository.api_post(
            url, json_data=None, data=open(data_file_path, 'rb')
        )
        logging.info(
            'Created bitstream with name [%s] and id [%s]',
            data_file_name, js['id']
        )
        logging.debug(
            'Bitstream id [%s] metadata\n%s', js['id'], pformat(js)
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

    def get_metadata(self):
        url = '/items/' + str(self._id) + '/metadata'
        return self._repository.api_get(url)
