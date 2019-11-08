# -*- coding: utf-8 -*-
from cachecontrol import CacheControl

import os
import requests
import time
import logging

logger = logging.getLogger(__name__)

session = requests.Session()
session = CacheControl(session)
session.headers.update({"Accept": "application/json"})
session.auth = str(os.environ.get("PLONE_USER")), str(os.environ.get("PLONE_PASSWORD"))

RETRY_BASE = 333  # ms (will be multiplied by 3 every interval)
RETRY_MAX = 10000  # ms (ceiling time for retries)

STATES = {"mapping_fetched": 0}
MAPPING_TIMEOUT_SEK = 3600


def _full_url(path: str):
    return "/".join([str(os.environ.get("PLONE_SERVICE")), path.strip("/")])


def _schema_url():
    return "/".join(
        [
            str(os.environ.get("PLONE_SERVICE")),
            str(os.environ.get("PLONE_PATH")),
            "@cesp-schema",
        ]
    )


def fetch_content(path: str, timestamp: float):
    url = _full_url(path)
    logger.info("fetch content from {0}".format(url))
    resp = session.get(url)
    return resp.json()


def fetch_schema(refetch: bool = False):
    # from celery.contrib import rdb; rdb.set_trace()
    if refetch or time.time() + MAPPING_TIMEOUT_SEK > STATES["mapping_fetched"]:
        url = _schema_url()
        logger.info("fetch content from {0}".format(url))
        resp = session.get(url)
        return resp.json()
    return


def fetch_binary(url: str):
    resp = session.get(url)
    return resp.content
