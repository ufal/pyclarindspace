# coding=utf-8
import os
import logging
from ._utils import urlopen, urlretrieve, urljoin
from pprint import pformat
_logger = logging.getLogger("clarindspace")


class item(object):
    """
        DSpace item representation. Holds name, id & handle; methods to add bitstreams
    """

    def __init__(self, name, item_id, handle, owning_collection, repository=None):
        """Constructor for Item"""
        self._name = name
        self._id = item_id
        self._handle = handle
        self._repository = repository
        self._owning_collection = owning_collection
        self._metadata = None

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
        try:
            root = ET.fromstring(metadata)
        except ET.ParseError:
            # is CMDI metadata available?
            _logger.warning("Received ill-formed metadata!")
            return []

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

    def add_bitstream(self, data_file_path, mime_type=None, data_file_name=None):
        """
            Upload file located at data_file_path to item
        """
        if data_file_name is None:
            # get file name; used as the bitstream name & for format detection
            data_file_name = os.path.basename(data_file_path)

        url = '/items/' + str(self._id) + '/bitstreams?name=' + data_file_name
        if mime_type is not None:
            url += "&file_mime_type=%s" % mime_type

        with open(data_file_path, 'rb') as f:
            js = self._repository.api_post(url, json_data=None, data=f)

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

    def add_metadata(self, json_metadata_entry_array):
        """Add metadata entries"""
        self._repository.api_post(
            '/items/' + str(self._id) + '/metadata', json_metadata_entry_array, parse_json=False)
        logging.info('Successfully added metadata to item [%s].', self._id)

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
        if not self._metadata:
            self._metadata = self._repository.api_get(url)
        return self._metadata

    def bitstreams(self, limit=20, offset=0):
        url = '/items/' + str(self._id) + '/bitstreams' + '?limit=' + str(limit) + '&offset=' + str(offset)
        return self._repository.api_get(url)

    def delete_bitstreams(self, id_str):
        url = '/items/' + str(self._id) + '/bitstreams/' + str(id_str)
        return self._repository.api_delete(url)

    def create_new_version(self):
        """Creates a new item as a version of this"""
        # will reuse the metadata (cleanup needed)
        cleaned_up_metadata = item.cleanup_metadata_for_copy(
            self.get_metadata(), ' v2.0')
        # finally add note
        cleaned_up_metadata.append(
            {'key': 'local.submission.note', 'value': 'Thise item is a new version of ' + self.handle})
        # prepare replaces field
        cleaned_up_metadata.append(
            {'key': 'dc.relation.replaces', 'value': 'http://hdl.handle.net/' + self.handle})
        new_version = self._owning_collection.create_item(cleaned_up_metadata)
        # update self with isreplacedby seems not needed, probably triggered by presence of dc.relation.replaces
        # self.add_metadata([{'key': 'dc.relation.isreplacedby', 'value': 'http://hdl.handle.net/' + new_version.handle}])
        return new_version

    def create_related_item(self):
        """Creates a new item based on this links them through dc.relation"""
        # will reuse the metadata (cleanup needed)
        cleaned_up_metadata = item.cleanup_metadata_for_copy(
            self.get_metadata(), ' (related item)')
        # finally add note
        cleaned_up_metadata.append(
            {'key': 'local.submission.note', 'value': 'Thise item is related to ' + self.handle})
        # add relation to the new item
        cleaned_up_metadata.append(
            {'key': 'dc.relation', 'value': 'http://hdl.handle.net/' + self.handle})
        related_item = self._owning_collection.create_item(cleaned_up_metadata)
        # update self with dc.relation
        self.add_metadata(
            [{'key': 'dc.relation', 'value': 'http://hdl.handle.net/' + related_item.handle}])
        return related_item

    @staticmethod
    def cleanup_metadata_for_copy(metadata, append_to_title):
        # see
        # https://github.com/ufal/clarin-dspace/blob/clarin/dspace-xmlui/src/main/java/cz/cuni/mff/ufal/dspace/app/xmlui/aspect/submission/submit/AddNewVersionAction.java
        omit_keys = ('dc.identifier.uri', 'dc.date.accessioned', 'dc.date.available', 'dc.description.provenance',
                     'local.featuredService', 'local.submission.note', 'dc.relation.replaces',
                     'dc.relation.isreplacedby', 'local.branding')
        cleaned_up_metadata = []
        for obj in metadata:
            if obj['key'] == 'dc.title':
                obj['value'] += append_to_title
            elif obj['key'] in omit_keys:
                continue
            cleaned_up_metadata.append(obj)

        return cleaned_up_metadata

    def download_bitstreams(self, limit=20, offset=0):
        arr = self.bitstreams(limit, offset)
        local_files = []
        for b in arr:
            file_name = self._repository.api_download(b["retrieveLink"])
            local_files.append(file_name)
        return local_files

    @staticmethod
    def metadata(key, value, lang=None):
        return {
            "key": key,
            "value": value,
            "language": lang
        }
