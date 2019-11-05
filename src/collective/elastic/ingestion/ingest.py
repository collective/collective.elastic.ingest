# -*- coding: utf-8 -*-

from collective.elastic.ingest.mapping import create_or_update_mapping


def ingest(content, full_schema, index_name):
    create_or_update_mapping(full_schema, index_name)
