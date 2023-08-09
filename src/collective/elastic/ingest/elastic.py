# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
from opensearchpy import OpenSearch

import os

from .logging import logger
from collective.elastic.ingest import version_elasticsearch, ELASTICSEARCH_7


def get_ingest_client():
    """return elasticsearch client for.ingest"""
    OPENSEARCH_INGEST_SERVER = os.environ.get("OPENSEARCH_INGEST_SERVER")
    logger.debug(f"** OPENSEARCH_INGEST_SERVER {OPENSEARCH_INGEST_SERVER}")

    raw_addr = os.environ.get(
        "OPENSEARCH_INGEST_SERVER",
        os.environ.get("ELASTICSEARCH_INGEST_SERVER", "http://localhost:9200"))
    use_ssl = os.environ.get(
        "OPENSEARCH_INGEST_USE_SSL",
        os.environ.get("ELASTICSEARCH_INGEST_USE_SSL", "0"))
    use_ssl = bool(int(use_ssl))
    addresses = [x for x in raw_addr.split(",") if x.strip()]
    if not addresses:
        addresses.append("127.0.0.1:9200")
    if OPENSEARCH_INGEST_SERVER:
        """
         TODO Documentation about when to use more than one
         ElasticSearch or OpenSearch cluster
        """
        (host, port) = addresses[0].rsplit(":", 1)
        logger.debug(f"host {host}")
        logger.debug(f"port {port}")
        auth = (
            os.environ.get("OPENSEARCH_INGEST_LOGIN", 'admin'),
            os.environ.get("OPENSEARCH_INGEST_PASSWORD", 'admin'))
        logger.debug(f"auth {auth}")
        logger.debug(f"use_ssl {use_ssl}")
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
