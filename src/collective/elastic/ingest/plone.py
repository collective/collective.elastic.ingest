from .logging import logger
from cachecontrol import CacheControl

import os
import requests
import time


session = requests.Session()
session = CacheControl(session)
session.headers.update({"Accept": "application/json"})
session.auth = str(os.environ.get("PLONE_USER")), str(os.environ.get("PLONE_PASSWORD"))

RETRIES_STATUS_MAX = 4
RETRY_STATUS_BASE = 1  # seconds

RETRIES_TIMESTAMP_MAX = 10
RETRY_TIMESTAMP_BASE = 0.33333  # seconds

STATES = {"mapping_fetched": 0}
MAPPING_TIMEOUT_SEK = 60  # seconds


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
    url = f"{_full_url(path)}?expand=collectiveelastic"
    retries_timestamp = 0
    delay_timestamp = RETRY_TIMESTAMP_BASE
    retries_status = 0
    delay_status = RETRY_STATUS_BASE
    while True:
        logger.info(
            "fetch content ({}) from {} ".format(
                1 + retries_timestamp + retries_status, url
            )
        )
        resp = session.get(url)
        # xxx: move status retry to HTTPAdapter/ulrib3 retry
        if resp.status_code != 200:
            if retries_status > RETRIES_STATUS_MAX:
                logger.info(
                    "-> status {} - retry no.{}, wait {:0.3f}s".format(
                        resp.status_code, retries_status, delay_status
                    )
                )
                break
            time.sleep(delay_status)
            delay_status += delay_status
            retries_status += 1
        result = resp.json()
        if (
            not result
            or "@components" not in result
            or "collectiveelastic" not in result["@components"]
            or result["@components"]["collectiveelastic"]["last_indexing_queued"]
            < timestamp
        ):
            if retries_timestamp > RETRIES_TIMESTAMP_MAX:
                break
            logger.info(
                "-> timestamp retry - fetch no.{}, wait {:0.3f}s".format(
                    retries_timestamp, delay_timestamp
                )
            )
            retries_timestamp += 1
            time.sleep(delay_timestamp)
            delay_timestamp += delay_timestamp
            continue
        return result

    logger.error("-> can not fetch content {}".format(url))


def fetch_schema(refetch=False):
    # from celery.contrib import rdb; rdb.set_trace()
    if refetch or time.time() + MAPPING_TIMEOUT_SEK > STATES["mapping_fetched"]:
        url = _schema_url()
        logger.info("fetch full schema from {}".format(url))
        resp = session.get(url)
        # xxx: check resp here
        STATES["mapping_fetched"] = time.time()
        return resp.json()
    return


def fetch_binary(url):
    logger.info("fetch binary data from {}".format(url))
    resp = session.get(url)
    # xxx: check resp here
    return resp.content
