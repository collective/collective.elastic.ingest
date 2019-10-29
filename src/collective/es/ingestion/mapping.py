# -*- coding: utf-8 -*-
from collective.es.ingestion.elastic import get_ingest_client
from elasticsearch.exceptions import TransportError

import logging
import operator
import time


logger = logging.getLogger(__name__)

FIELDMAP = {"": ""}


def _cache_key(fun, index_name):
    return (int(time.time() / 3), index_name)


def get_mapping(index_name):
    es = get_ingest_client()
    if es is None:
        logger.warning("No ElasticSearch client available.")
        return

    try:
        mapping = es.indices.get_mapping(index=index_name)
    except TransportError as e:
        if e.status_code == 404:
            es.indices.create(index=index_name)
            mapping = es.indices.get_mapping(index=index_name)
        else:
            raise
    return mapping


def _iterate_schema(full_schema):
    for section_name, section in sorted(full_schema.items(), operator.itemgetter(0)):
        for field_name, field_type in sorted(section.items(), operator.itemgetter(0)):
            yield section_name, field_name, field_type


def create_or_update_mapping(full_schema, index_name):
    import pdb; pdb.set_trace()
    mapping = get_mapping(index_name)
    for section_name, field_name, field_type in _iterate_schema(full_schema):
        target_type = FIELDMAP.get(field_type, None)
        if target_type is None:
            logger.warning("{0} field type not in map, ignore.".format(field_type))
            continue
        # full_field_name = "{0}.{1}".format(section_name, field_name)
        if field_name in mapping:
            if mapping[field_name] != target_type:
                logger.warning(
                    "field {0} duplicate with different types "
                    "(existing={1}, new={2}), ignore.".format(
                        field_name, mapping[field_name], target_type
                    )
                )
                continue
            mapping[fieldname] = target_type
