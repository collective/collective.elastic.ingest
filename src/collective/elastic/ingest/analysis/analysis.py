# -*- coding: utf-8 -*-
"""TODO
- Recap if analysis settings should better be updated on Celery /Plone reboot,
    but not on every _doc update.
- Read lexicon from lexicon.txt
"""
from ..elastic import get_ingest_client
from ..logging import logger

import json
import os

_analysis_file = os.environ.get(
    "ANALYSIS_FILE", os.path.join(os.path.dirname(__file__), "analysis.json")
)
print("** Looking for _analysis_file", _analysis_file)

try:
    with open(_analysis_file, mode="r") as fp:
        ANALYSISMAP = json.load(fp)
except FileNotFoundError:
    ANALYSISMAP = None


def update_analysis(index_name):
    """Provide elasticsearch with analyzers to be used in mapping.

    Sample is found in analysis.json.example.
    Overwrite with your analyzers by creating an ANALYSIS_FILE `analysis.json`.
    See README for details.

    First `update_analysis` then `create_or_update_mapping`:
    Mapping can use analyzers from analysis.json.
    """
    if ANALYSISMAP:
        es = get_ingest_client()
        if es is None:
            logger.warning("No ElasticSearch client available.")
            return

        index_exists = es.indices.exists(index_name)
        if not index_exists:
            logger.warning("No ElasticSearch index available.")
            return

        # process analysis
        analysis_settings = ANALYSISMAP.get("settings", {})
        if analysis_settings:
            logger.info("Update settings with analyzers.")
            es.indices.close(index=index_name)
            es.indices.put_settings(index=index_name, body=analysis_settings)
            es.indices.open(index=index_name)

    else:
        logger.info("No analyzer configuration found.")
