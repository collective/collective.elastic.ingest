# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch

import os


def get_ingest_client():
    """return elasticsearch client for ingestion
    """
    raw_addr = os.environ.get("ELASTICSEARCH_INGEST_SERVER", "http://localhost:9200")
    use_ssl = os.environ.get("ELASTICSEARCH_INGEST_USE_SSL", "0")
    use_ssl = bool(int(use_ssl))
    addresses = [x for x in raw_addr.split(",") if x.strip()]
    if not addresses:
        addresses.append("127.0.0.1:9200")
    return Elasticsearch(
        addresses,
        use_ssl=use_ssl,
        # here some more params need to be configured.
    )
