# coding=utf-8
import logging
from clarindspace import item, handle
import pprint
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
_logger = logging.getLogger()

if __name__ == '__main__':
    for pid in (
        "http://hdl.handle.net/11346/TEST--HGGA",
    ):
        h = handle(pid)
        _logger.info(pprint.pformat(h.handle_metadata(True)))
        arr = item.bitstream_info_from_pid(pid)
