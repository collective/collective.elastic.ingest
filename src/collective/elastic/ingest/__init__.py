try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version


version_elasticsearch = version("elasticsearch")
ELASTICSEARCH_7 = int(version_elasticsearch[0]) <= 7

version_opensearchpy = version("opensearch-py")
OPENSEARCH_2 = int(version_opensearchpy[0]) <= 2
