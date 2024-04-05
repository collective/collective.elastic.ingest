from .client import get_client
from .logging import logger


def delete_index(index_name):
    client = get_client()
    if client is None:
        logger.warning("No index client available.")
        return
    try:
        client.indices.delete(index=index_name)
    except Exception as e:
        logger.exception(str(e))
