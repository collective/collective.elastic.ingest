from .logging import logger

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


def get_analysis():
    """Provide mapping analyzers to be used in mapping.

    Sample is found in analysis.json.example.
    Overwrite with your analyzers by creating an ANALYSIS_FILE `analysis.json`.
    See README for details.

    """
    if not ANALYSISMAP:
        logger.info("No analyzer configuration given.")
        return
    analysis_settings = ANALYSISMAP.get("settings", {}).get("analysis", None)
    if not analysis_settings:
        logger.info(f"No valid analyzer settings found in file {_analysis_file}.")
        return
    return analysis_settings
