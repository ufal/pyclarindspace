# coding=utf-8
import logging
import os
from pprint import pformat
import sys
from .._item import item
from .._repository import repository

__debug = os.environ.get('DEBUG', 'False') == 'True'
logging_level = logging.INFO if not __debug else logging.DEBUG
logging.basicConfig(format='%(asctime)s %(message)s', level=logging_level)
logging.debug('Set log level to [%s]', logging_level)
_logger = logging.getLogger()


class ViadatItem(item):

    def __init__(self, metadata_dict, collection):
        if not self.metadata_valid(self.__class__.md_fields, metadata_dict):
            raise ValueError('Invalid metadata')
        else:
            backing_item = collection.create_item(ViadatItem.metadata_convert(metadata_dict))
            self._name = backing_item.name
            self._id = backing_item.id
            self._handle = backing_item.handle
            self._owning_collection = collection
            self._repository = backing_item._repository

    @property
    def repository(self):
        return self._repository

    def metadata_valid(self, md_fields, metadata_dict, only_required=False):
        if not isinstance(metadata_dict, dict):
            sys.exit("metadata_dict should be a dictionary not a " + type(metadata_dict))
        reguired_missing = []
        for md_field in md_fields:
            if md_field.get('required', False) and metadata_dict.get(md_field['name'], None) is None:
                reguired_missing.append(md_field['name'])
        bad_names = []
        if not only_required:
            whitelisted_keys = list(map(lambda x: x['name'], md_fields))
            for key in metadata_dict.keys():
                if key not in whitelisted_keys:
                    bad_names.append(key)
        if not(len(reguired_missing) == 0 and len(bad_names) == 0):
            _logger.error('Offending keys - required missing: %s, not in whitelist: %s.\nThe '
                          'whitelist is %s', pformat(reguired_missing), pformat(bad_names),
                          pformat(whitelisted_keys))
            return False
        else:
            return True

    @staticmethod
    def metadata_convert(metadata_dict):
        """Convert dict to expected key value array, we ignore lang"""
        return [item.metadata(key, value) for key, value in metadata_dict.items()]


class Interview(ViadatItem):
    md_fields = [{'name': key, 'required': True} for key in [
        'dc.title', 'dc.language.iso', 'dc.identifier', 'viadat.interview.date',
        'dc.type', 'dc.rights.uri', 'dc.rights', 'dc.rights.label'
    ]] + [{'name': key, 'required': False} for key in ['viadat.interview.transcript',
                                                       'viadat.interview.date',
                                                       'viadat.interview.length',
                                                       'viadat.interview.place',
                                                       'viadat.interview.interviewer',
                                                       'dc.description',
                                                       'dc.relation.ispartof',
                                                       'viadat.interview.keywords',
                                                       'viadat.interview.detailedKeywords',
                                                       'viadat.interview.period',
                                                       'viadat.interview.type',
                                                       'viadat.interview.note']]


class Narrator(ViadatItem):
    md_fields = [{'name': key, 'required': True} for key in [
        'dc.title', 'viadat.narrator.birthdate', 'dc.identifier', 'dc.type', 'dc.rights.uri',
        'dc.rights', 'dc.rights.label'
    ]] + [{'name': key, 'required': False} for key in {'viadat.narrator.alias',
                                                       'viadat.narrator.gender',
                                                       'viadat.narrator.birthdate',
                                                       'viadat.narrator.project',
                                                       'viadat.narrator.degree',
                                                       'viadat.narrator.keywordsProfession',
                                                       'viadat.narrator.keywordsTopic',
                                                       'viadat.narrator.consent',
                                                       'viadat.narrator.contact',
                                                       'viadat.narrator.note',
                                                       'viadat.narrator.outputs',
                                                       'viadat.narrator.materials'}]

    def create_interview(self, metadata_dict):
        metadata_dict['dc.relation.ispartof'] = 'http://hdl.handle.net/' + self.handle
        return Interview(metadata_dict, self.repository.interviews)


class ViadatRepo(repository):

    def __init__(self, base_url):
        super(ViadatRepo, self).__init__(base_url)
        self._narrators_col = None
        self._interview_col = None
        self._inited = False

    @property
    def interviews(self):
        return self._interview_col

    @property
    def narrators(self):
        return self._narrators_col

    def _setup(self):
        com = self.find_community_by_name('VIADAT')
        self._narrators_col = com.find_collection_by_name('Narrators')
        self._interview_col = com.find_collection_by_name('Interviews')
        if self._narrators_col is None or self._interview_col is None:
            sys.exit('Narrators or Intervies collection not found in the repository.\nQuitting.')
        self._inited = True

    def create_narrator(self, metadata_dict):
        if not self._inited:
            self._setup()
        metadata_dict['dc.type'] = 'narrator'
        return Narrator(metadata_dict, self.narrators)
