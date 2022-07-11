try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version

version_elasticsearch = version("elasticsearch")
ELASTICSEARCH_7 = int(version_elasticsearch[0]) <= 7
