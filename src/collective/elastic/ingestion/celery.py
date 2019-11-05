# -*- coding: utf-8 -*-
from .ingest import ingest
from .plone import fetch_content
from .plone import fetch_schema
from .removal import remove
from celery import Celery

import logging
import os


logger = logging.getLogger(__name__)

app = Celery("collective.elastic.ingest", broker=os.environ.get("CELERY_BROKER"))


@app.task(name="collective.elastic.ingest.index")
def index(path, timestamp, index_name):
    try:
        content = fetch_content(path, timestamp)
    except Exception:
        msg = "Error while fetching content from Plone"
        logger.exception(msg)
        return msg
    try:
        schema = fetch_schema()
    except Exception:
        msg = "Error while fetching schema from Plone"
        logger.exception(msg)
        return msg
    except Exception:
        logger.exception("")
    try:
        ingest(content, schema, index_name)
    except Exception:
        msg = "Error while writing data to ElasticSearch"
        logger.exception(msg)
        return msg
    return "indexed {0} on timestamp {1}".format(path, timestamp)


@app.task(name="collective.elastic.ingest.unindex")
def unindex(uid, index_name):
    try:
        remove(uid, index_name)
    except Exception:
        msg = "Error while removing data from ElasticSearch"
        logger.exception(msg)
        return msg
    return "unindexed {0}".format(uid)
