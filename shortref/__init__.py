# coding=utf-8
import logging
from pprint import pformat
import requests


class handle(object):
    """
        Shortref api object
    """
    API_URL = 'https://lindat.mff.cuni.cz/services/shortener/api/v1/handles'

    @staticmethod
    def mint(target_url, title, reportemail, subprefix):
        """ 
            Register the target_url with shortref and return the handle
        """
        response = requests.post(
            handle.API_URL,
            json={
                'url': target_url,
                'reportemail': reportemail,
                'title': title,
                'subprefix': subprefix
            }
        )
        logging.debug(pformat(response))
        response.raise_for_status()
        js = response.json()
        logging.info(
            'Successfully created handle [%s] for [%s]', js[
                'handle'], target_url
        )
        logging.debug(pformat(js))
        return js['handle']
