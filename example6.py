# coding=utf-8
import logging
import os
import sys
import json
from pprint import pformat
__debug = os.environ.get('DEBUG', 'False') == 'True'
logging_level = logging.INFO if not __debug else logging.DEBUG
logging.basicConfig(
    format='%(asctime)s %(filename)s:%(lineno)s %(message)s', level=logging_level)
logging.debug('Set log level to [%s]', logging_level)
_logger = logging.getLogger()
import clarindspace
from clarindspace import imports


if __name__ == '__main__':
    """
        The first argument should be a mapfile in json format that connects
        metadata file with data file e.g.,
        ```
            {
              "urn-nbn-fi-csc-kata20160308114458775736.xml": "HYY_PAR_1min_2009.csv",
              "urn-nbn-fi-csc-kata20170425121500649018.xml": "KUM_Tower_WDIR_32m_1min_2015.csv"
            }

        ```
    """
    if len(sys.argv) != 2 or not os.path.exists(sys.argv[1]):
        _logger.warning("Expecting mapfile")
        sys.exit(1)

    # read mapfile
    mapfile = sys.argv[1]
    mapfile_dir = os.path.dirname(mapfile)
    with open(mapfile, mode="r") as fin:
        data_map = json.load(fin)

    ingest_d = {}

    # update paths, check if files exist
    for metadata_file, file_paths in data_map.items():
        _logger.info(
            u"Preparing [%s] with [%d] bitstream(s).",
            os.path.basename(metadata_file),
            len(file_paths)
        )
        metadata_file = os.path.join(mapfile_dir, metadata_file)
        file_paths = [os.path.join(mapfile_dir, x) for x in file_paths]
        for file_path in [metadata_file] + file_paths:
            if not os.path.exists(file_path):
                _logger.critical(u"File [%s] does not exist", file_path)
                sys.exit(1)

        _logger.info(u"Loading [%s]", metadata_file)
        importer = imports.example_rdf(metadata_file)
        m_arr = importer.parse_to_dspace_triples()
        ingest_d[metadata_file] = (m_arr, file_paths)

    # Use admin account a) creating com & col b) no hassle with user rights
    # management
    REPO_URL = os.environ.get('REPO_URL') or "https://rda-summerschool.csc.fi/repository/"
    ADMIN_EMAIL = os.environ.get('EMAIL')
    ADMIN_PASS = os.environ.get('PASSWORD')
    _logger.info(
        "Using [%s] as repository url and [%s] user", REPO_URL, ADMIN_EMAIL
    )
    if REPO_URL is None or ADMIN_EMAIL is None:
        _logger.warning("Expecting non null values for url, email")
        sys.exit(1)

    # login
    repository = clarindspace.repository(REPO_URL)
    repository.login(ADMIN_EMAIL, ADMIN_PASS)
    _logger.info(pformat(repository.login_status()))

    # find/create community by name
    community = repository.find_or_create_community('RDA community')
    _logger.debug(pformat(community.id))

    # find/create collection
    collection = community.find_or_create_collection('RDA collection')
    _logger.debug(pformat(collection.id))

    items = [x for x in collection.items()]

    # import items from the provided dir
    for _1, (m_arr, file_paths) in ingest_d.items():
        title = [x["value"] for x in m_arr if x["key"] == "dc.title"][0]
        for item in items:
            if item.name == title:
                _logger.info(pformat(item.get_metadata()))
                bis = item.bitstreams()
                for i in bis:
                    item.delete_bitstreams(i["id"])
                for file_path in file_paths:
                    _1, suffix = os.path.splitext(file_path)
                    if suffix == ".csv":
                        mimetype = "text/csv"
                    item.add_bitstream(file_path, mimetype)
        continue
    repository.logout()
