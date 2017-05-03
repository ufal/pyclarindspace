import logging
from pprint import pformat
import requests


class Shortref(object):
    """Shortref api object"""
    SHORTREF_API_URL = 'https://lindat.mff.cuni.cz/services/shortener/api/v1/handles'

    @staticmethod
    def obtain_handle(target_url, title, reportemail, subprefix):
        """register the target_url with shortref and return the handle"""
        response = requests.post(Shortref.SHORTREF_API_URL,
                                 json={'url': target_url, 'reportemail': reportemail,
                                       'title': title, 'subprefix': subprefix})
        logging.debug(pformat(response))
        response.raise_for_status()
        shortref_object = response.json()
        logging.info('Successfully created handle "%s" for "%s"', shortref_object['handle'],
                     target_url)
        logging.debug(pformat(shortref_object))
        return shortref_object['handle']
