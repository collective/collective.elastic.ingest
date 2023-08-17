# -*- coding: utf-8 -*-
from ..elastic import get_ingest_client
from ..logging import logger

from collective.elastic.ingest import ELASTICSEARCH_7, OPENSEARCH_2

import json
import os

OPENSEARCH = True if os.environ.get("OPENSEARCH") else False

_analysis_file = os.environ.get(
    "ANALYSIS_FILE", os.path.join(os.path.dirname(__file__), "analysis.json")
)

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

    First `update_analysis`, then `create_or_update_mapping`:
    Mapping can use analyzers from analysis.json.
    """

    if ANALYSISMAP:
        analysis_settings = ANALYSISMAP.get("settings", {})
        if analysis_settings:
            es = get_ingest_client()
            if es is None:
                logger.warning("No ElasticSearch client available.")
                return
            if ELASTICSEARCH_7:
                index_exists = es.indices.exists(index_name)
            else:
                index_exists = es.indices.exists(index=index_name)
            if index_exists:
                return

            logger.info(
                f"Create index '{index_name}' with analysis settings "
                f"from '{_analysis_file}', but without mapping."
            )
            if not OPENSEARCH and ELASTICSEARCH_7 or OPENSEARCH and OPENSEARCH_2:
                es.indices.create(index_name, body=ANALYSISMAP)
            else:
                es.indices.create(index=index_name, settings=analysis_settings)
            return

    logger.info("No analyzer configuration found.")
