# -*- coding: utf-8 -*-
from .logging import logger
from cachecontrol import CacheControl

import os
import requests
import time


session = requests.Session()
session = CacheControl(session)
session.headers.update({"Accept": "application/json"})
session.auth = str(os.environ.get("PLONE_USER")), str(os.environ.get("PLONE_PASSWORD"))

RETRY_BASE = 333  # ms (will be multiplied by 3 every interval)
RETRY_MAX = 10000  # ms (ceiling time for retries)

STATES = {"mapping_fetched": 0}
MAPPING_TIMEOUT_SEK = 3600


def _full_url(path):
    return "/".join([str(os.environ.get("PLONE_SERVICE")), path.strip("/")])


def _schema_url():
    return "/".join(
        [
            str(os.environ.get("PLONE_SERVICE")),
            str(os.environ.get("PLONE_PATH")),
            "@cesp-schema",
        ]
    )


def fetch_content(path, timestamp):
    url = _full_url(path)
    retries = 0
    delay = 0.5
    while retries < 5:
        logger.info("fetch content from {0} retry {1}".format(url, retries))
        resp = session.get(url)
        # xxx: check resp here
        result = resp.json()
        if (
            not result
            or "@components" not in result
            or "last_indexing_queued" not in result["@components"]
            or result["@components"]["last_indexing_queued"] < timestamp
        ):
            logger.info("retry fetch {0}, wait {1}s".format(url, delay))
            retries += 1
            time.sleep(delay)
            delay += delay
            continue
        return result

    logger.error("can not fetch content {0}".format(url, delay))


def fetch_schema(refetch=False):
    # from celery.contrib import rdb; rdb.set_trace()
    if refetch or time.time() + MAPPING_TIMEOUT_SEK > STATES["mapping_fetched"]:
        url = _schema_url()
        logger.info("fetch full schema from {0}".format(url))
        resp = session.get(url)
        # xxx: check resp here
        return resp.json()
    return


def fetch_binary(url):
    logger.info("fetch binary data from {0}".format(url))
    resp = session.get(url)
    # xxx: check resp here
    return resp.content
