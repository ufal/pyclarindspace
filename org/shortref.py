import requests
import logging
from pprint import pformat


class Shortref(object):
    """Shortref api object"""
    SHORTREF_API_URL = 'https://lindat.mff.cuni.cz/services/shortener/api/v1/handles'

    @staticmethod
    def obtain_handle(target_url, title, reportemail, subprefix):
        """register the target_url with shortref and return the handle"""
        r = requests.post(Shortref.SHORTREF_API_URL,
                          json={'url': target_url, 'reportemail': reportemail,
                                'title': title, 'subprefix': subprefix})
        logging.debug(pformat(r))
        r.raise_for_status()
        shortref_object = r.json()
        logging.info('Successfully created handle "{}" for "{}"'.format(shortref_object[
                                                                            'handle'], target_url))
        logging.debug(pformat(shortref_object))
        return shortref_object['handle']
