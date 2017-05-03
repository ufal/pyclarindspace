import logging
import os
import json
from pprint import pformat
import sys
from clarin_dspace import Repository
from org.shortref import Shortref


REPO_URL = os.environ.get('REPO_URL')
# Use admin account a) creating com & col b) no hassle with user rights mgmt
ADMIN_EMAIL = os.environ.get('EMAIL')
ADMIN_PASS = os.environ.get('PASSWORD')

debug = os.environ.get('DEBUG', 'False') == 'True'

if debug:
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Set log level to {0}'.format(logging.getLevelName(logging.getLogger(__name__)
                                                                    .getEffectiveLevel())))

if __name__ == '__main__':
    items_dir = sys.argv[1]

    # login
    repository = Repository(REPO_URL)
    repository.login(ADMIN_EMAIL, ADMIN_PASS)
    logging.debug(pformat(repository.login_status()))

    # find/create community by name
    community = repository.find_or_create_community('test community')
    logging.debug(pformat(community.id))

    # find/create collection
    collection = community.find_or_create_collection('test collection')
    logging.debug(pformat(collection.id))

    # import items from the provided dir
    for subdir in os.listdir(os.path.abspath(items_dir)):
        absPath = os.path.abspath(items_dir + '/' + subdir)
        # load metadata
        with open(absPath + '/item_metadata.json') as f:
            metadata = json.load(f)
        # load filelist containing files to be uploaded
        with open(absPath + '/filelist.txt') as f:
            files = f.readlines()
        # process the filelist, stripping endlines, converting to absolute path
        files = [os.path.abspath(x.strip()) for x in files]
        my_item = collection.create_item(metadata)
        logging.debug(pformat(my_item))
        for file in files:
            my_item.add_bitstream(file)

        # convert item 'internal' handle to landing page url
        target_url = REPO_URL + '/xmlui/handle/' + my_item.handle
        title = my_item.name
        reportemail = ADMIN_EMAIL
        subprefix = 'TEST'

        handle = Shortref.obtain_handle(target_url, title, reportemail, subprefix)
        logging.debug(handle)
        my_item.update_identifier(handle)

    repository.logout()
