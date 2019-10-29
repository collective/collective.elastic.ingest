# -*- coding: utf-8 -*-
from cachecontrol import CacheControl

import os
import requests

session = requests.Session()
session = CacheControl(session)
session.headers.update({"Accept": "application/json"})
session.auth = (os.environ.get("PLONE_USER"), os.environ.get("PLONE_PASSWORD"))

RETRY_BASE = 333  # ms (will be multiplied by 3 every interval)
RETRY_MAX = 10000  # ms (ceiling time for retries)


def _full_url(path):
    "/".join([os.environ.get("PLONE_BASE_URL"), path])


def _schema_url(path):
    "/".join([os.environ.get("PLONE_BASE_URL"), "@cesp-schema"])


def fetch_content(path, timestamp):
    resp = session.get(_full_url(path))
    return resp.json


def fetch_schema():
    resp = session.get(_schema_url())
    return resp.json
