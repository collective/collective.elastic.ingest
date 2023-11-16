from .client import get_client
from .logging import logger


def get_ingest_client(elasticsearch_server_baseurl=None):
    # to be removed in a 3.x release
    logger.warn(".elastic.get_client is deprecated, use .client.get_client instead")
    return get_client(elasticsearch_server_baseurl)
