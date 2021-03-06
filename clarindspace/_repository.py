# coding=utf-8
import logging
import re
import requests
from pprint import pformat
from ._community import community
from ._collection import collection
from ._item import item
from ._utils import urljoin

_logger = logging.getLogger("clarindspace")


class repository(object):
    """
        Represent and access repository content
    """

    def __init__(self, base_url):
        """
            Args:
                base_url (str): The repository url up to /rest or /xmlui
        """
        self._base_url = base_url
        self._api_url = urljoin(base_url, 'rest/')
        self._token = None
        self._request_headers = None

    def api_get(self, url):
        """ http get """
        api_url = urljoin(self._api_url, url.lstrip("/"))
        r = requests.get(api_url, headers=self._request_headers)
        _logger.debug(pformat(r))
        r.raise_for_status()
        return r.json()

    def api_post(self, url, json_data, headers_update=None, parse_json=True, **kwargs):
        """ http post """
        args = {
            "headers": self._request_headers,
            "json": json_data
        }
        if headers_update is not None:
            h = self._request_headers.copy()
            h.update(headers_update)
            args["headers"] = h

        args.update(kwargs)
        api_url = urljoin(self._api_url, url.lstrip("/"))
        r = requests.post(api_url, **args)
        _logger.debug(pformat(r))
        try:
            r.raise_for_status()
        except:
            raise
        return r.json() if parse_json else r.text

    def api_put(self, url, data):
        """ http put """
        api_url = urljoin(self._api_url, url.lstrip("/"))
        r = requests.put(
            api_url, json=data, headers=self._request_headers
        )
        _logger.debug(pformat(r))
        r.raise_for_status()
        return r.text

    def api_delete(self, url):
        """ http put """
        api_url = urljoin(self._api_url, url.lstrip("/"))
        r = requests.delete(
            api_url, headers=self._request_headers
        )
        _logger.debug(pformat(r))
        r.raise_for_status()
        return r.text

    def api_download(self, url):
        """ streaming GET using content disposition """
        api_url = urljoin(self._api_url, url.lstrip("/"))
        with requests.get(api_url, headers=self._request_headers, stream=True) as r:
            r.raise_for_status()
            cd_match = re.findall('filename=["\']?([^"\']+)', r.headers.get('content-disposition', ''))
            if len(cd_match) > 0:
                filename = cd_match[0]
            else:
                filename = api_url.split('/', 1)[1].split('?')[0]
            with open(filename, 'wb') as downloaded_file:
                for chunk in r.iter_content(chunk_size=None):
                    if chunk:
                        downloaded_file.write(chunk)
        return filename

    def login(self, email, password):
        """ Obtain access token for user with provided email and password """
        self._token = self.api_post(
            '/login', {'email': email, 'password': password}, parse_json=False)
        _logger.info("User [%s] successfully logged in", email)
        self._request_headers = {
            'rest-dspace-token': self._token,
            'Accept': 'application/json'
        }

    def login_status(self):
        """ Returns the json of /rest/status - useful for debugging """
        js = self.api_get('/status')
        return js

    def find_community_by_name(self, name):
        """
            Fetch all communities and do exact match on the name.
            Return `community` object
        """
        js = self.api_get('/communities')
        coms = {com['name']: com['id'] for com in js}
        _logger.debug(pformat(coms))
        if name not in coms:
            _logger.info('Community [%s] not found', name)
            return None
        return community(name, coms[name], self)

    def create_community(self, name):
        """
            Create a community as the logged in user, no check whether the give name exists
        """
        js = self.api_post('/communities', {'name': name})
        _logger.info(
            'Created community with name [%s] and id [%s]', name, js['id']
        )
        return community(name, js['id'], self)

    def find_or_create_community(self, name):
        """Search for community by name and if fail create new one with that name"""
        com = self.find_community_by_name(name)
        return com if com is not None else self.create_community(name)

    def find_item(self, pid):
        """Search for item based on provided pid"""
        # DS-3671 * not treated as wildcard in /find-by-metadata-field
        # workaround null
        # workaround empty string
        items = self.find_items_by_metadata('dc.identifier.uri', pid) or \
                self.find_items_by_metadata('dc.identifier.uri', pid, None) or \
                self.find_items_by_metadata('dc.identifier.uri', pid, "")
        if len(items) > 0:
            return items[0]
        else:
            return None

    def find_items_by_metadata(self, field, exact_value, lang='*'):
        try:
            js = self.api_post(
                '/items/find-by-metadata-field?expand=parentCollection',
                item.metadata(field, exact_value, lang)
            )

            return [item(js_item['name'], js_item['id'], js_item['handle'],
                         collection(js_item['parentCollection']['name'],
                                    js_item['parentCollection']['id'],
                                    self),
                         self)
                    for js_item in js]
        except:
            pass
        return []

    def logout(self):
        self.api_post('/logout', None, parse_json=False)
        _logger.info("User successfully logged out")
