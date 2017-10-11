# coding=utf-8
import logging
import os

import sys

import clarindspace
from pprint import pformat
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.WARNING)
_logger = logging.getLogger()

if __name__ == '__main__':
    REPO_URL = os.environ.get(
        'REPO_URL') or "https://rda-summerschool.csc.fi/repository/"
    repository = clarindspace.repository(REPO_URL)

    community_name = sys.argv[1] if 1 < len(sys.argv) else 'RDA community'
    community = repository.find_community_by_name(community_name)
    if community is None:
        logging.warning("Did not find the specified community!")
        sys.exit(1)

    collection_name = sys.argv[2] if 2 < len(sys.argv) else 'RDA collection'
    collection = community.find_collection_by_name(collection_name)
    if collection is None:
        logging.warning("Did not find the specified collection!")
        sys.exit(1)

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
    logging.warning("Found [%d] urls:\n%s" % (
        len(bitstream_urls), pformat(bitstream_urls)
    ))
