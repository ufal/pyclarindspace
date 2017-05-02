import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import logging
import os
import json

from pprint import pformat

import sys

SHORTREF_API_URL = 'https://lindat.mff.cuni.cz/services/shortener/api/v1/handles'
REPO_URL = os.environ.get('REPO_URL')
REPO_API_URL= REPO_URL + '/rest'
#Use admin account a) creating com & col b) no hassle with user rights mgmt
ADMIN_EMAIL = os.environ.get('EMAIL')
ADMIN_PASS = os.environ.get('PASSWORD')

debug = os.environ.get('DEBUG', 'False') == 'True'

if debug:
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Set log level to {0}'.format(logging.getLevelName(logging.getLogger(__name__).getEffectiveLevel())))


def login(email, password):
    r = requests.post(REPO_API_URL + '/login', json={'email': email, 'password': password})
    logging.debug(pformat(r))
    r.raise_for_status()
    return r.text


def login_status(request_headers):
    r = requests.get(REPO_API_URL + '/status', headers=request_headers)
    logging.debug(pformat(r))
    r.raise_for_status()
    return r.json()


def create_community(community_name, request_headers):
    url = REPO_API_URL + '/communities'
    r = requests.get(url, headers=request_headers)
    logging.debug(pformat(r))
    r.raise_for_status()
    communities = {community['name']: community['id'] for (community) in r.json()}
    #   list(map(lambda community: community['name'], r.json()))
    logging.debug(pformat(communities))
    if community_name in communities:
        #sys.exit('Community "' + community_name + '" already exists!')
        return communities[community_name]

    community = {'name': community_name}
    r = requests.post(url, json=community, headers=request_headers)
    logging.debug(pformat(r))
    r.raise_for_status()
    community = r.json()
    return community['id']


def create_collection(community_id, collection_name, request_headers):
    url = REPO_API_URL + '/communities/' + str(community_id) + '/collections'
    r = requests.get(url, headers=request_headers)
    logging.debug(pformat(r))
    r.raise_for_status()
    collections = {collection['name']: collection['id'] for (collection) in r.json()}
    logging.debug(pformat(collections))
    if collection_name in collections:
        # sys.exit('collection "' + collection_name + '" already exists!')
        return collections[collection_name]

    collection = {'name': collection_name}
    r = requests.post(url, json=collection, headers=request_headers)
    logging.debug(pformat(r))
    r.raise_for_status()
    collection = r.json()
    return collection['id']


def create_item(collection_id, item_metadata, request_headers):
    url = REPO_API_URL + '/collections/' + str(collection_id) + '/items'
    item = {'metadata': item_metadata}
    r = requests.post(url, json=item, headers=request_headers)
    logging.debug(pformat(r))
    r.raise_for_status()
    #item = r.json()
    #return item['id']
    return r.json()


def add_bitstream(item_id, data_file_path, request_headers):
    data_file_name = os.path.basename(data_file_path)
    url = REPO_API_URL + '/items/' + str(item_id) + '/bitstreams?name=' + data_file_name
    m = MultipartEncoder([('filename', open(data_file_path, 'rb'))])
    request_headers = request_headers.copy()
    request_headers['Content-Type'] = m.content_type
    r = requests.post(url, data=m, headers=request_headers)
    logging.debug(pformat(r))
    r.raise_for_status()
    bitstream = r.json()
    logging.debug(pformat(bitstream))


def obtain_shortref_handle(item):
    #landing page
    shortref_target_url = REPO_URL + '/xmlui/handle/' + item['handle']
    title = item['name']
    reportemail = ADMIN_EMAIL
    subprefix = 'TEST'
    r = requests.post(SHORTREF_API_URL, json={'url': shortref_target_url, 'reportemail': reportemail, 'title': title,
                                              'subprefix': subprefix})
    logging.debug(pformat(r))
    r.raise_for_status()
    shortref_object = r.json()
    logging.debug(pformat(shortref_object))
    return shortref_object['handle']


def update_identifier(item, handle, request_headers):
    url = REPO_API_URL + '/items/' + str(item['id']) + '/metadata'
    r = requests.put(url, json=[{'key': 'dc.identifier.uri', 'value': handle, 'language': None}], headers=request_headers)
    logging.debug(pformat(r))
    r.raise_for_status()


if __name__ == '__main__':
    items_dir = sys.argv[1]

    #login to api
    access_token = login(ADMIN_EMAIL, ADMIN_PASS)
    headers = {'rest-dspace-token': access_token, 'Accept': 'application/json'}
    logging.debug(pformat(login_status(headers)))

    #import items
    for subdir in os.listdir(os.path.abspath(items_dir)):
        absPath = os.path.abspath(items_dir + '/' + subdir)
        with open(absPath + '/item_metadata.json') as f:
            metadata = json.load(f)
        with open(absPath + '/filelist.txt') as f:
            files = f.readlines()
        files = [os.path.abspath(x.strip()) for x in files]
        community_id = create_community('test community', headers)
        logging.debug(pformat(community_id))
        collection_id = create_collection(community_id, 'test collection', headers)
        logging.debug(pformat(collection_id))
        my_item = create_item(collection_id, metadata, headers)
        logging.debug(pformat(my_item))
        item_id = my_item['id']
        logging.debug(pformat(item_id))
        for file in files:
            add_bitstream(item_id, file, headers)

        handle = obtain_shortref_handle(my_item)
        logging.debug(handle)
        update_identifier(my_item, handle, headers)



