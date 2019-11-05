# -*- coding: utf-8 -*-
from cachecontrol import CacheControl

import os
import requests
import time


session = requests.Session()
session = CacheControl(session)
session.headers.update({"Accept": "application/json"})
session.auth = (os.environ.get("PLONE_USER"), os.environ.get("PLONE_PASSWORD"))

RETRY_BASE = 333  # ms (will be multiplied by 3 every interval)
RETRY_MAX = 10000  # ms (ceiling time for retries)

STATES = {
    'mapping_fetched': 0,
}
MAPPING_TIMEOUT_SEK = 3600


def _full_url(path):
    return "/".join([os.environ.get("PLONE_BASE_URL"), path])


def _schema_url():
    return "/".join([os.environ.get("PLONE_BASE_URL"), "@cesp-schema"])


def fetch_content(path, timestamp):
    resp = session.get(_full_url(path))
    return resp.json()


def fetch_schema(refetch=False):
    if refetch or time.time() + MAPPING_TIMEOUT_SEK > STATES["mapping_fetched"]:
        resp = session.get(_schema_url())
        return resp.json()
    return
