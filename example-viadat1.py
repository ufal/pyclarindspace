# coding=utf-8
import logging
import os
from pprint import pformat
import sys
from clarindspace.viadat import ViadatRepo

__debug = os.environ.get('DEBUG', 'False') == 'True'
logging_level = logging.INFO if not __debug else logging.DEBUG
logging.basicConfig(format='%(asctime)s %(message)s', level=logging_level)
logging.debug('Set log level to [%s]', logging_level)
_logger = logging.getLogger()


if __name__ == '__main__':
    # Use admin account a) creating com & col b) no hassle with user rights
    # management
    ADMIN_EMAIL = os.environ.get('EMAIL', 'dspace@lindat.cz')
    ADMIN_PASS = os.environ.get('PASSWORD', 'dspace')
    REPO_URL = os.environ.get('REPO_URL', 'http://localhost:8080')
    _logger.info("Using [%s] as repository url and [%s] user",
                 REPO_URL, ADMIN_EMAIL)
    if REPO_URL is None or ADMIN_EMAIL is None:
        _logger.warning("Expecting non null values for url, email")
        sys.exit(1)

    repository = ViadatRepo(REPO_URL)
    repository.login(ADMIN_EMAIL, ADMIN_PASS)
    _logger.info(pformat(repository.login_status()))
    kj2 = {'dc.title': 'REST Erben, Karel Jaromír', 'viadat.narrator.birthdate': '1845',
           'viadat.narrator.identifier': 'kj2_rest'}
    narrator = repository.create_narrator(kj2)
    kj2_i1 = {'dc.title': 'REST interview', 'dc.language.iso': 'ces',
              'viadat.interview.identifier': 'kj2_rest_i1', 'viadat.interview.date': '1901-01-01'}
    interview = narrator.create_interview(kj2_i1)
    repository.logout()
