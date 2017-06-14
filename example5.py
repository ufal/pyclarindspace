# coding=utf-8
import logging
import os
import clarindspace
from pprint import pformat
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.WARNING)
_logger = logging.getLogger()

if __name__ == '__main__':
    REPO_URL = os.environ.get('REPO_URL') or "https://rda-summerschool.csc.fi/repository/"
    ADMIN_EMAIL = os.environ.get('EMAIL')
    ADMIN_PASS = os.environ.get('PASSWORD')

    repository = clarindspace.repository(REPO_URL)
    repository.login(ADMIN_EMAIL, ADMIN_PASS)

    item = repository.find_item("http://hdl.handle.net/21.T11998/3728")
    arr = item.download_bitstreams()

    item = repository.find_item("http://hdl.handle.net/21.T11998/34937")
    print(pformat(item.get_metadata()))

    item.add_metadata(
        [clarindspace.item.metadata('dc.relation', '...')]
    )
    item.replace_metadata_field(
        [clarindspace.item.metadata('dc.relation', 'xxx')]
    )

    # item_new_version = item.create_new_version()
    item_new_version = item.create_related_item()

    pass