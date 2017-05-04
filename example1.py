# coding=utf-8
import logging
import os
import json
from pprint import pformat
import sys
import clarindspace
from shortref import handle

__debug = os.environ.get('DEBUG', 'False') == 'True'
logging_level = logging.INFO if not __debug else logging.DEBUG
logging.basicConfig(format='%(asctime)s %(message)s', level=logging_level)
logging.debug('Set log level to [%s]', logging_level)
_logger = logging.getLogger()


if __name__ == '__main__':
    if len(sys.argv) != 2 or not os.path.exists(sys.argv[1]):
        _logger.warning("Expecting path to a directory with items")
        sys.exit(1)
    items_dir = sys.argv[1]

    # Use admin account a) creating com & col b) no hassle with user rights
    # management
    ADMIN_EMAIL = os.environ.get('EMAIL')
    ADMIN_PASS = os.environ.get('PASSWORD')
    REPO_URL = os.environ.get('REPO_URL')
    _logger.info("Using [%s] as repository url and [%s] user",
                 REPO_URL, ADMIN_EMAIL)
    if REPO_URL is None or ADMIN_EMAIL is None:
        _logger.warning("Expecting non null values for url, email")
        sys.exit(1)

    # login
    repository = clarindspace.repository(REPO_URL)
    repository.login(ADMIN_EMAIL, ADMIN_PASS)
    _logger.info(pformat(repository.login_status()))

    # find/create community by name
    community = repository.find_or_create_community('test community')
    _logger.debug(pformat(community.id))

    # find/create collection
    collection = community.find_or_create_collection('test collection')
    _logger.debug(pformat(collection.id))

    # import items from the provided dir
    for subdir in os.listdir(os.path.abspath(items_dir)):
        abs_path = os.path.abspath(os.path.join(items_dir, subdir))
        # load metadata
        with open(os.path.join(abs_path, 'item_metadata.json'), mode="r") as f:
            metadata = json.load(f)
        # load filelist containing files to be uploaded
        with open(os.path.join(abs_path, 'filelist.txt'), mode="r") as f:
            files = [os.path.join(abs_path, x.strip()) for x in f.readlines()]
        # process the filelist, stripping endlines, converting to absolute path
        submitted_item = collection.create_item(metadata)
        _logger.debug(pformat(submitted_item))
        for file_path in files:
            submitted_item.add_bitstream(file_path)

        # convert item 'internal' handle to landing page url
        target_url = REPO_URL + '/xmlui/handle/' + submitted_item.handle
        subprefix = 'TEST'
        hdl = handle.mint(target_url, submitted_item.name,
                          ADMIN_EMAIL, subprefix)
        _logger.debug(hdl)
        submitted_item.update_identifier(hdl)

    repository.logout()
