# -*- coding: utf-8 -*-

from collective.es.ingestion.mapping import get_mapping


def ingest(content, mapping, index_name):
    current_mapping = get_mapping()
