# coding=utf-8
import logging
import os
import sys
import json
from pprint import pformat
import clarindspace
from clarindspace import imports

__debug = os.environ.get('DEBUG', 'False') == 'True'
logging_level = logging.INFO if not __debug else logging.DEBUG
logging.basicConfig(format='%(asctime)s %(message)s', level=logging_level)
logging.debug('Set log level to [%s]', logging_level)
_logger = logging.getLogger()


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
    for metadata_file, file_paths in data_map.iteritems():
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
        if len(file_paths) > 0:
            m_arr.append(importer.triple("local.has.files", "yes"))
            m_arr.append(importer.triple("local.files.count", len(file_paths)))
        ingest_d[metadata_file] = (m_arr, file_paths)

    # Use admin account a) creating com & col b) no hassle with user rights
    # management
    ADMIN_EMAIL = os.environ.get('EMAIL')
    ADMIN_PASS = os.environ.get('PASSWORD')
    REPO_URL = os.environ.get('REPO_URL')
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

    # import items from the provided dir
    for _1, (m_arr, file_paths) in ingest_d.iteritems():
        submitted_item = collection.create_item(m_arr)
        _logger.debug(pformat(submitted_item))
        for file_path in file_paths:
            mimetype = None
            _1, suffix = os.path.splitext(file_path)
            if suffix == ".csv":
                mimetype = "text/csv"

            submitted_item.add_bitstream(file_path, mimetype)

    repository.logout()
