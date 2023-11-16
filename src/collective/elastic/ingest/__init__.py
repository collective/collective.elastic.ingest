from importlib.metadata import version

import os


OPENSEARCH = os.environ.get("INDEX_OPENSEARCH") == "1"

if OPENSEARCH:
    version_opensearchpy = version("opensearch-py")
    if int(version_opensearchpy[0]) < 2:
        raise ValueError(
            "opensearch-py 1.x is not supported, use version 1.x of the collective.elastic.ingest package."
        )
else:
    version_elasticsearch = version("elasticsearch")
    if int(version_elasticsearch[0]) < 7:
        raise ValueError(
            "elasticsearch < 7 is not supported, use Version 1.x of the collective.elastic.ingest package."
        )
