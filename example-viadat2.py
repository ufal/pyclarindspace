# coding=utf-8
import csv
import glob
import logging
import os
from pprint import pformat
import sys
import lxml.etree as etree
from clarindspace.viadat import ViadatRepo, ViadatItem

__debug = os.environ.get('DEBUG', 'False') == 'True'
logging_level = logging.INFO if not __debug else logging.DEBUG
logging.basicConfig(format='%(asctime)s %(message)s', level=logging_level)
logging.debug('Set log level to [%s]', logging_level)
_logger = logging.getLogger()


def xml_metadata_to_json(xml_path):
    document = etree.parse(os.path.expanduser(xml_path))
    schema = document.xpath('/dublin_core/@schema')[0]
    ret = dict()
    for child_el in document.findall('dcvalue'):
        key = '{}.{}.{}'.format(schema, child_el.get('element'), child_el.get('qualifier')) if \
            child_el.get('qualifier', '') != "none" else '{}.{}'.format(schema,
                                                                        child_el.get('element'))
        if key in ret:
            val = ret[key]
            if isinstance(val, list):
                val.append(child_el.text)
            else:
                values = [val, child_el.text]
                ret[key] = values
        else:
            ret[key] = child_el.text
    return ret


def process_contents_file(contents_path):
    if os.path.isfile(contents_path):
        with open(contents_path) as contents_in:
            contents = csv.reader(contents_in, delimiter='\t')
            contents_dir = os.path.dirname(contents_path)
            return [(os.path.join(contents_dir, row[0]), {el.split(':')[0]:el.split(':')[1] for el in row[1:]}) for row in contents]
    else:
        return []


def _read_item_metadata(imports_dir, item_dir):
    metadata = {}
    for metadata_file in glob.glob(os.path.join(imports_dir, item_dir, '*.xml')):
        _logger.debug("processing file {}".format(metadata_file))
        file_name = os.path.basename(metadata_file)
        if file_name == 'dublin_core.xml' or file_name.startswith(
                'metadata_'):  # dublin_core.xml, metadata_*.xml
            _logger.debug("reading metadata {}".format(metadata_file))
            metadata.update(xml_metadata_to_json(metadata_file))
    return metadata


def _read_bitstream_metadata(file_path):
    bitstream_metadata = {}
    for metadata_file in glob.glob(os.path.join(imports_dir, item_dir,
                                                os.path.basename(file_path) + '_*.xml')):
        bitstream_metadata.update(xml_metadata_to_json(metadata_file))
    return bitstream_metadata


def _import_bitstreams(imports_dir, item_dir, item):
    files_and_attrs = process_contents_file(os.path.join(imports_dir, item_dir, 'contents'))
    for file_path, attrs in files_and_attrs:
        bitstream_metadata = _read_bitstream_metadata(file_path)
        item.add_bitstream(file_path, metadata=ViadatItem.metadata_convert(bitstream_metadata),
                           **attrs)


if __name__ == '__main__':
    # Use admin account a) creating com & col b) no hassle with user rights
    # management
    ADMIN_EMAIL = os.environ.get('EMAIL', 'dspace@lindat.cz')
    ADMIN_PASS = os.environ.get('PASSWORD', 'dspace')
    REPO_URL = os.environ.get('REPO_URL', 'http://localhost:8080')
    _logger.info("Using [%s] as repository url and [%s] user",
                 REPO_URL, ADMIN_EMAIL)
    if REPO_URL is None or ADMIN_EMAIL is None:
        _logger.warning("Expecting non null values for url, email")
        sys.exit(1)

    repository = ViadatRepo(REPO_URL)
    repository.login(ADMIN_EMAIL, ADMIN_PASS)
    _logger.info(pformat(repository.login_status()))

    # path to aip
    # narrator 2 interview mapping
    # xml metadata reader
    # create
    imports_dir = os.path.expanduser(sys.argv[1])
    narrators = {}
    interviews_md = {}
    for item_dir in [listed for listed in os.listdir(imports_dir) if os.path.isdir(
            os.path.join(imports_dir, listed))]:
        metadata = _read_item_metadata(imports_dir, item_dir)
        # _logger.debug(pformat(metadata))
        if metadata['dc.type'] == 'narrator':
            narrators[item_dir] = repository.create_narrator(metadata)
            _import_bitstreams(imports_dir, item_dir, narrators[item_dir])
        elif metadata['dc.type'] == 'interview':
            interviews_md[item_dir] = metadata
        else:
            sys.exit('Unknown dc.type {}'.format(metadata['dc.type']))
    with open(os.path.join(imports_dir, 'narrator2interviews.txt')) as mapping_file:
        lines = mapping_file.read().splitlines()
        for line in lines:
            narrator_dir, interview_dirs = line.split(':')
            if interview_dirs:
                narrator = narrators[narrator_dir]
                for interview_dir in interview_dirs.split(','):
                    interview = narrator.create_interview(interviews_md[interview_dir])
                    _import_bitstreams(imports_dir, interview_dir, interview)
    repository.logout()
