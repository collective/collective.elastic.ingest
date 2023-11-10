from importlib.metadata import version

import os


OPENSEARCH = os.environ.get("OPENSEARCH") == "1"

version_elasticsearch = version("elasticsearch")
ELASTICSEARCH_7 = int(version_elasticsearch[0]) <= 7

version_opensearchpy = version("opensearch-py")
OPENSEARCH_2 = int(version_opensearchpy[0]) <= 2
