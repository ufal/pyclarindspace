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

    # test login/logout
    repository = clarindspace.repository(REPO_URL)
    repository.login(ADMIN_EMAIL, ADMIN_PASS)
    _logger.info(pformat(repository.login_status()))
    repository.logout()
