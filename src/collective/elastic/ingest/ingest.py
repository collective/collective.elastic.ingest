# -*- coding: utf-8 -*-

from collective.elastic.ingest.mapping import create_or_update_mapping
from collective.elastic.ingest.mapping import setup_ingest_pipelines
from collections import OrderedDict

KEYS_TO_REMOVE = [
    'items',
    'items_total',
    'parent',
    '@components',
]


STATES = {
    'pipelines_created': False,
}

PREPROCESSORS = OrderedDict()


def rid_leverage(content, key):
    content['rid'] = content['@components']['catalog_rid']


PREPROCESSORS['rid_leverage'] = rid_leverage


# removals
def remove_entry(content, key):
    del content[key]


PREPROCESSORS['@components'] = remove_entry
PREPROCESSORS['@id'] = remove_entry
PREPROCESSORS['items'] = remove_entry
PREPROCESSORS['items_total'] = remove_entry
PREPROCESSORS['parent'] = remove_entry
PREPROCESSORS['version'] = remove_entry
PREPROCESSORS['versioning_enabled'] = remove_entry


def extract_binary(content, key):
    """
    """
    pass


PREPROCESSORS['binary'] = extract_binary


def ingest(content, full_schema, index_name):
    if full_schema:
        if not STATES["pipelines_created"]:
            setup_ingest_pipelines(full_schema, index_name)
            STATES["pipelines_created"] = True
        create_or_update_mapping(full_schema, index_name)

    # preprocess content
    for key, preprocessor in PREPROCESSORS.items():
        preprocessor(content, key)

    # todo
