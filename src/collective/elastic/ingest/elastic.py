# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version

import os

version_elasticsearch = version("elasticsearch")


def get_ingest_client():
    """return elasticsearch client for.ingest"""
    raw_addr = os.environ.get("ELASTICSEARCH_INGEST_SERVER", "http://localhost:9200")
    use_ssl = os.environ.get("ELASTICSEARCH_INGEST_USE_SSL", "0")
    use_ssl = bool(int(use_ssl))
    addresses = [x for x in raw_addr.split(",") if x.strip()]
    if not addresses:
        addresses.append("127.0.0.1:9200")
    if int(version_elasticsearch[0]) <= 7:
        return Elasticsearch(
            addresses,
            use_ssl=use_ssl,
        )
    return Elasticsearch(addresses)
