# coding=utf-8
import logging
import re
import sys
from builtins import str as text
from pprint import pformat
try:
    import rdflib
except:
    print "Library rdflib is not installed - execute `pip install rdflib`"
    sys.exit(0)

_logger = logging.getLogger("clarindspace")


class example_rdf(object):
    """
        Use simple mapping from rdf to clarin-dspace compatible metadata formats.
    """

    _map = {
        "http://purl.org/dc/terms/title": "dc.title",
        "http://purl.org/dc/terms/description": "dc.description",
        "http://purl.org/dc/terms/issued": "dc.date.issued",
        "http://purl.org/dc/terms/identifier": "dc.identifier.other",
        "http://www.w3.org/ns/dcat#downloadURL": "dc.identifier.other",
        "http://xmlns.com/foaf/0.1/homepage": "dc.source.uri",
        "http://purl.org/dc/terms/publisher": (
            "dc.publisher",
            None,
            "_get_name"
        ),
        "http://purl.org/dc/terms/RightsStatement": (
            "dc.rights.uri",
            re.compile("<RightsDeclaration>(.*)</RightsDeclaration>"),
            "_rights_fixer"
        ),
    }

    def __init__(self, file_str):
        self._rdf_metadata = rdflib.Graph().parse(file_str)
        pass

    def parse_to_dspace_triples(self):
        """
            This is an example with several places hardcoded.
        """
        m_arr = []
        triples = [(str(x[0]), str(x[1]), x[2]) for x in self._rdf_metadata]
        for subj, pred, obj in triples:
            # print "%20s %20s %s" % (subj, pred, obj)
            k = example_rdf._map.get(str(pred), None)
            if k is not None:
                v = text(obj)
                if isinstance(k, tuple):
                    k, rec, value_norm = k
                    if rec is not None:
                        m = rec.search(v)
                        if not m:
                            continue
                        v = m.group(1)
                    v = getattr(self, value_norm)(v, triples)
                if v is not None and len(v) > 0:
                    m_arr.append(self.triple(k, text(v).strip()))

        # specific touches - should be updated based on imported data
        d = dict([(x["key"], x["value"]) for x in m_arr])
        if "dc.rights.uri" in d:
            # fill out others required if not present
            if "dc.rights" not in d:
                m_arr.append(self.triple("dc.rights", d["dc.rights.uri"]))
            if "dc.rights.label" not in d:
                val = "PUB" if "creativecommons" in d["dc.rights.uri"] else ""
                m_arr.append(self.triple("dc.rights.label", val))
        if "dc.type" not in d:
            m_arr.append(self.triple("dc.type", "numeric-set"))

        d = dict([(x["key"], x["value"]) for x in m_arr])
        _logger.debug("Extracted keys [%s]", ",".join(d.keys()))
        return m_arr

    def triple(self, key, value, lang=None):
        return {
            "key": key,
            "value": value,
            "language": lang
        }

    @staticmethod
    def _rights_fixer(val, *args, **kwargs):
        """
            We use http ids in clarin-dspace.
        """
        if val.startswith("https://creativecommons.org"):
            return val.replace("https://", "http://")
        return val

    @staticmethod
    def _get_name(val, triples, **kwargs):
        """
            Get value from id
        """
        for subj, pred, obj in triples:
            if subj == val and pred == "http://xmlns.com/foaf/0.1/name":
                return obj
        return None
