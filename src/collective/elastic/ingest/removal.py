# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .elastic import get_ingest_client

import logging


logger = logging.getLogger(__name__)


def remove(uid, index_name):
    es = get_ingest_client()
    if es is None:
        logger.warning("No ElasticSearch client available.")
        return
    try:
        es.delete(index=index_name, doc_type="content", id=uid)
    except Exception:
        logger.exception(
            "unindexing of {0} on index {1} failed".format(uid, index_name)
        )
