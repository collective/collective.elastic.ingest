from . import OPENSEARCH
from .logging import logger

import os


if OPENSEARCH:
    from opensearchpy import OpenSearch
else:
    from elasticsearch import Elasticsearch


def get_client(index_server_baseurl: str = ""):
    """index client for query or ingest

    either OpenSearch or Elasticsearch client, depending on OPENSEARCH env var
    """

    raw_addr = index_server_baseurl or os.environ.get("INDEX_SERVER", "")
    use_ssl = bool(int(os.environ.get("INDEX_USE_SSL", "0")))
    addresses = [x for x in raw_addr.split(",") if x.strip()]
    if not addresses:
        addresses.append("127.0.0.1:9200")

    # TODO: more auth options (cert, bearer token, api-key, etc)
    auth = (
        os.environ.get("INDEX_LOGIN", "admin"),
        os.environ.get("INDEX_PASSWORD", "admin"),
    )

    if OPENSEARCH:
        logger.info(f"Use OpenSearch client at {addresses}")
        hosts = []
        for address in addresses:
            host, port = address.rsplit(":", 1)
            hosts.append({"host": host, "port": port})
        client = OpenSearch(
            hosts=hosts,
            http_auth=auth,
            use_ssl=use_ssl,
            verify_certs=False,
        )
        info = client.info()
        logger.info(f"OpenSearch client info: {info}")
    else:
        logger.info(f"Use ElasticSearch client at {addresses}")
        client = Elasticsearch(
            addresses,
            use_ssl=use_ssl,
            basic_auth=auth,
            verify_certs=False,
        )
    return client
