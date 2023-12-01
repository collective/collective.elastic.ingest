from .ingestion import process_ingest
from .logging import logger
from .plone import fetch_content
from .plone import fetch_schema
from .removal import remove
from celery import Celery

import os


# sentry integration
sentry_dsn = os.environ.get("SENTRY_DSN", None)
sentry_ingest = os.environ.get("SENTRY_INGEST", "false") == "true"
if sentry_dsn and sentry_ingest:
    try:
        from sentry_sdk.integrations.celery import CeleryIntegration

        import sentry_sdk

        sentry_sdk.init(sentry_dsn, integrations=[CeleryIntegration()])
        logger.debug("Enable sentry logging.")
        sentry_project = os.environ.get("SENTRY_PROJECT", None)
        if sentry_project is not None:
            with sentry_sdk.configure_scope() as scope:
                scope.set_tag("project", sentry_project)
    except ImportError:
        logger.exception(
            "sentry-logging configured, but package sentry_dsn not installed.\n"
            "try: pip install sentry_dsn"
        )
        raise

# configure tasks
app = Celery("collective.elastic.ingest", broker=os.environ.get("CELERY_BROKER"))


@app.task(name="collective.elastic.ingest.index")
def index(path, timestamp, index_name):
    try:
        content = fetch_content(path, timestamp)
    except Exception:
        msg = "Error while fetching content from Plone"
        # xxx: retry handling!
        logger.exception(msg)
        return msg
    if content is None:
        return
    try:
        schema = fetch_schema()
    except Exception:
        msg = "Error while fetching schema from Plone"
        logger.exception(msg)
        return msg
    try:
        process_ingest(content, schema, index_name)
    except Exception:
        # xxx: retry handling!
        msg = "Error while writing data to ElasticSearch"
        logger.exception(msg)
        return msg
    return "indexed {} on timestamp {}".format(path, timestamp)


@app.task(name="collective.elastic.ingest.unindex")
def unindex(uid, index_name):
    try:
        remove(uid, index_name)
    except Exception:
        # xxx: retry handling!
        msg = "Error while removing data from ElasticSearch"
        logger.exception(msg)
        return msg
    return "unindexed {}".format(uid)
