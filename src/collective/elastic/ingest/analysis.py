from .elastic import get_ingest_client
from .logging import logger
from collective.elastic.ingest import OPENSEARCH

import json
import os


_analysis_file = os.environ.get("ANALYSIS_FILE", None)


ANALYSISMAP = None
if _analysis_file:
    try:
        with open(_analysis_file) as fp:
            ANALYSISMAP = json.load(fp)
    except FileNotFoundError:
        logger.warning(f"Analysis file '{_analysis_file}' not found.")
else:
    logger.info("No analysis file configured.")


def update_analysis(index_name):
    """Provide elasticsearch with analyzers to be used in mapping.

    Sample is found in analysis.json.example.
    Overwrite with your analyzers by creating an ANALYSIS_FILE `analysis.json`.
    See README for details.

    First `update_analysis`, then `create_or_update_mapping`:
    Mapping can use analyzers from analysis.json.
    """

    if not ANALYSISMAP:
        logger.info("No analyzer configuration given.")
        return
    analysis_settings = ANALYSISMAP.get("settings", {})
    if not analysis_settings:
        logger.warning("No analyzer settings found in configuration.")
        return
    es = get_ingest_client()
    if es is None:
        logger.warning("No ElasticSearch client available.")
        return
    if es.indices.exists(index_name):
        logger.debug(
            f"Analysis for index '{index_name}' already exists, skip creation."
        )
        return
    logger.info(
        f"Create index '{index_name}' with analysis settings "
        f"from '{_analysis_file}', but without mapping."
    )
    es.indices.create(index_name, body=ANALYSISMAP)
