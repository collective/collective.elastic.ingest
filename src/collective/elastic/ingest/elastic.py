# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
from opensearchpy import OpenSearch

import os

from .logging import logger
from collective.elastic.ingest import \
    version_elasticsearch, ELASTICSEARCH_7

OPENSEARCH = True if os.environ.get("OPENSEARCH") else False


def get_ingest_client(elasticsearch_server_baseurl=None):
    """return elasticsearch client for.ingest"""

    raw_addr = elasticsearch_server_baseurl or os.environ.get(
        "ELASTICSEARCH_INGEST_SERVER", "http://localhost:9200")
    use_ssl = os.environ.get("ELASTICSEARCH_INGEST_USE_SSL", "0")
    use_ssl = bool(int(use_ssl))
    addresses = [x for x in raw_addr.split(",") if x.strip()]
    if not addresses:
        addresses.append("127.0.0.1:9200")
    if OPENSEARCH:
        """
         TODO Documentation about when to use more than one
         ElasticSearch or OpenSearch cluster
        """
        (host, port) = addresses[0].rsplit(":", 1)
        auth = (
            os.environ.get("ELASTICSEARCH_INGEST_LOGIN", 'admin'),
            os.environ.get("ELASTICSEARCH_INGEST_PASSWORD", 'admin'))
        client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_auth=auth,
            use_ssl=use_ssl,
            verify_certs=False
        )
        info = client.info()
        logger.info(f"OpenSearch client info: {info}")
        return client
    elif ELASTICSEARCH_7:
        logger.info(f"ElasticSearch version {version_elasticsearch} installed")
        return Elasticsearch(
            addresses,
            use_ssl=use_ssl,
        )
    return Elasticsearch(addresses)
