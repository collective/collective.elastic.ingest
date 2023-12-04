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
    """return the full url to fetch the content from

    the path is the getPhysicalPath of the content object
    It is prefixed with the path to the plone site, like "Plone/en/about-us".

    Now we have three ways to configure the plone site prefix:
    1. keep - Directly with site prefix (default)
    2. strip - behind Virtual Host Monster with stripped site prefix
    """
    path = path.strip("/")
    plone_base_url = str(os.environ.get("PLONE_SERVICE")).strip("/")
    prefix_handling = str(os.environ.get("PLONE_SITE_PREFIX_METHOD", "keep")).strip()
    if prefix_handling == "keep":
        return "/".join([plone_base_url, path])

    if prefix_handling == "strip":
        prefix_path = str(os.environ.get("PLONE_SITE_PREFIX_PATH")).strip("/")
        path_parts = path.split("/")[len(prefix_path.split("/")) :]
        return "/".join([plone_base_url] + path_parts)

    raise ValueError(
        f"PLONE_SITE_PREFIX_METHOD must be one of keep, strip or add, not {prefix_handling}"
    )


def _schema_url():
    """return the url to fetch the schema from"""
    url = [str(os.environ.get("PLONE_SERVICE"))]
    if str(os.environ.get("PLONE_SITE_PREFIX_METHOD", "keep")).strip() == "keep":
        url.append(str(os.environ.get("PLONE_SITE_PREFIX_PATH")))
    url.append("@cesp-schema")
    return "/".join(url)


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
        # xxx: move status retry to HTTPAdapter/urllib3 retry
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


def fetch_schema():
    if time.time() <= STATES["mapping_fetched"] + MAPPING_TIMEOUT_SEK:
        return
    url = _schema_url()
    logger.info("fetch full schema from {}".format(url))
    resp = session.get(url)
    # xxx: check resp here
    STATES["mapping_fetched"] = time.time()
    return resp.json()


def fetch_binary(url):
    logger.info("fetch binary data from {}".format(url))
    resp = session.get(url)
    # xxx: check resp here
    return resp.content
