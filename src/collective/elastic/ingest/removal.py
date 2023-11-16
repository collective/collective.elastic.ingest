from .client import get_client
from .logging import logger


def remove(uid, index_name):
    client = get_client()
    if client is None:
        logger.warning("No index client available.")
        return
    try:
        client.delete(index=index_name, id=uid)
    except Exception:
        logger.exception("unindexing of {} on index {} failed".format(uid, index_name))
