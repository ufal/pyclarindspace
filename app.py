import requests
import logging

from pprint import pformat

import sys

REPO_URL='https://ufal-point-dev.ms.mff.cuni.cz/dspace5l/rest'
#Use admin account a) creating com & col b) no hassle with user rights mgmt
ADMIN_EMAIL=
ADMIN_PASS=

debug = True

if debug:
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Set log level to {0}'.format(logging.getLevelName(logging.getLogger(__name__).getEffectiveLevel())))


def login(email, password):
    r = requests.post(REPO_URL + '/login', json={'email': email,'password': password})
    logging.debug(pformat(r))
    r.raise_for_status()
    return r.text


def login_status(request_headers):
    r = requests.get(REPO_URL + '/status', headers=request_headers)
    logging.debug(pformat(r))
    r.raise_for_status()
    return r.json()


def create_community(community_name, request_headers):
    url = REPO_URL + '/communities'
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
    url = REPO_URL + '/communities/' + str(community_id) + '/collections'
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
    url = REPO_URL + '/collections/' + str(collection_id) + '/items'
    item = {'metadata': item_metadata}
    r = requests.post(url, json=item, headers=request_headers)
    logging.debug(pformat(r))
    r.raise_for_status()
    item = r.json()
    return item['id']

def add_bitstream(item_id, data_file_path, access_token):
    pass


if __name__ == '__main__':
    access_token = login(ADMIN_EMAIL, ADMIN_PASS)
    headers = {'rest-dspace-token': access_token, 'Accept': 'application/json'}
    logging.debug(pformat(login_status(headers)))
    community_id = create_community('test community', headers)
    logging.debug(pformat(community_id))
    collection_id = create_collection(community_id, 'test collection', headers)
    logging.debug(pformat(collection_id))
    item_id = create_item(collection_id, [{'key': 'dc.title', 'value': 'Item through REST', 'language': None},
                                          {'key': 'dc.contributor.author', 'value': 'Rest, Ful', 'language': None}], headers)
    logging.debug(pformat(item_id))


