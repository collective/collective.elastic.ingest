# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch

import os

from .logging import logger
from collective.elastic.ingest import version_elasticsearch, ELASTICSEARCH_7


def get_ingest_client():
    """return elasticsearch client for.ingest"""
    raw_addr = os.environ.get("ELASTICSEARCH_INGEST_SERVER", "http://localhost:9200")
    use_ssl = os.environ.get("ELASTICSEARCH_INGEST_USE_SSL", "0")
    use_ssl = bool(int(use_ssl))
    addresses = [x for x in raw_addr.split(",") if x.strip()]
    if not addresses:
        addresses.append("127.0.0.1:9200")
    logger.info("elasticsearch version {} installed".format(version_elasticsearch))
    if ELASTICSEARCH_7:
        return Elasticsearch(
            addresses,
            use_ssl=use_ssl,
        )
    return Elasticsearch(addresses)
