# coding=utf-8
import logging
import os
import clarindspace
from pprint import pformat
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.WARNING)
_logger = logging.getLogger()

if __name__ == '__main__':
    REPO_URL = os.environ.get('REPO_URL') or "https://rda-summerschool.csc.fi/repository/"
    repository = clarindspace.repository(REPO_URL)
    community = repository.find_community_by_name('RDA community')
    collection = community.find_collection_by_name('RDA collection')
    pids = collection.items_pid()
    _logger.info(pformat(pids))
    bitstream_pids = []
    for p in pids:
        item_pids = clarindspace.item.bitstream_info_from_pid(p)
        bitstream_pids += item_pids
    bitstream_urls = sorted([
        url for mimetype, url in bitstream_pids
        if mimetype not in ("text/html", )
    ])
    logging.warning(pformat(bitstream_urls))