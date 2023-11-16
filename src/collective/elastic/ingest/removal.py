from .elastic import get_ingest_client
from .logging import logger


def remove(uid, index_name):
    es = get_ingest_client()
    if es is None:
        logger.warning("No ElasticSearch client available.")
        return
    try:
        es.delete(index=index_name, id=uid)
    except Exception:
        logger.exception("unindexing of {} on index {} failed".format(uid, index_name))
