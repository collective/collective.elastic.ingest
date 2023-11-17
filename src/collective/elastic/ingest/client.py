from . import OPENSEARCH
from .logging import logger

import os
import threading


if OPENSEARCH:
    from opensearchpy import OpenSearch
else:
    from elasticsearch import Elasticsearch

_local_storage = threading.local()


def get_client(index_server_baseurl: str = ""):
    """index client for query or ingest

    either OpenSearch or Elasticsearch client, depending on OPENSEARCH env var
    """

    client = getattr(_local_storage, "client", None)
    if client is not None:
        return _local_storage.client

    raw_addr = index_server_baseurl or os.environ.get("INDEX_SERVER", "")
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
        use_ssl = bool(int(os.environ.get("INDEX_USE_SSL", "0")))
        client = OpenSearch(
            hosts=hosts,
            http_auth=auth,
            use_ssl=use_ssl,
            verify_certs=False,
        )
        info = client.info()
        logger.info(f"OpenSearch client info: {info}")
    else:
        logger.info(f"Use ElasticSearch client at {addresses} with auth: {auth}")
        client = Elasticsearch(
            addresses,
            basic_auth=auth,
            verify_certs=False,
        )
    setattr(_local_storage, "client", client)
    return client
