from .logging import logger
from collective.elastic.ingest import OPENSEARCH

import os
import threading
import typing


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
        addresses.append("127.0.0.1:9200" if OPENSEARCH else "https://localhost:9200")

    # TODO: more auth options (cert, bearer token, api-key, etc)
    auth = (
        os.environ.get("INDEX_LOGIN", "admin"),
        os.environ.get("INDEX_PASSWORD", "admin"),
    )

    if OPENSEARCH:
        logger.info(f"Use OpenSearch client at {addresses}")
        kwargs: dict[str, typing.Any] = {
            "hosts": [
                dict(zip(("host", "port"), address.rsplit(":", 1)))
                for address in addresses
            ]
        }
        kwargs["use_ssl"] = bool(int(os.environ.get("INDEX_USE_SSL", "0")))
        if kwargs["use_ssl"]:
            kwargs["verify_certs"] = bool(
                int(os.environ.get("INDEX_VERIFY_CERTS", "0"))
            )
            kwargs["ssl_show_warn"] = bool(
                int(os.environ.get("INDEX_SSL_SHOW_WARN", "0"))
            )
            kwargs["ssl_assert_hostname"] = bool(
                int(os.environ.get("INDEX_SSL_ASSERT_HOSTNAME", "0"))
            )
        kwargs["http_auth"] = auth
        logger.info(f"OpenSearch client kwargs: {kwargs}")
        client = OpenSearch(**kwargs)
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
