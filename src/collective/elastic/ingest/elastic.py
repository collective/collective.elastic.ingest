from . import ELASTICSEARCH_7
from . import OPENSEARCH
from .logging import logger

import os


if OPENSEARCH:
    from opensearchpy import OpenSearch
else:
    from elasticsearch import Elasticsearch


def get_ingest_client(elasticsearch_server_baseurl=None):
    """return elasticsearch client for.ingest"""

    raw_addr = elasticsearch_server_baseurl or os.environ.get(
        "INGEST_SERVER", "http://localhost:9200"
    )
    use_ssl = os.environ.get("INGEST_USE_SSL", "0")
    use_ssl = bool(int(use_ssl))
    addresses = [x for x in raw_addr.split(",") if x.strip()]
    if not addresses:
        addresses.append("127.0.0.1:9200")

    if OPENSEARCH:
        hosts = []
        for address in addresses:
            host, port = address.rsplit(":", 1)
            hosts.append({"host": host, "port": port})
        auth = (
            os.environ.get("INGEST_LOGIN", "admin"),
            os.environ.get("INGEST_PASSWORD", "admin"),
        )
        client = OpenSearch(
            hosts=hosts,
            http_auth=auth,
            use_ssl=use_ssl,
            verify_certs=False,
        )
        info = client.info()
        logger.info(f"OpenSearch client info: {info}")
        return client
    elif ELASTICSEARCH_7:
        from . import version_elasticsearch

        logger.info(f"ElasticSearch version {version_elasticsearch} installed")
        return Elasticsearch(
            addresses,
            use_ssl=use_ssl,
        )
    return Elasticsearch(addresses)
