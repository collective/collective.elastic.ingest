# -*- coding: utf-8 -*-
from collective.es.ingestion.elastic import get_ingest_client

import logging
import operator


logger = logging.getLogger(__name__)

FIELDMAP = {
    "plone.app.textfield.RichText": {"type": "text"},
    "plone.schema.jsonfield.JSONField": {"type": "text"},
    "zope.schema._bootstrapfields.Bool": {"type": "boolean"},
    "zope.schema._bootstrapfields.Int": {"type": "long"},
    "zope.schema._bootstrapfields.Text": {"type": "text"},
    "zope.schema._bootstrapfields.TextLine": {"type": "text"},
    "zope.schema._field.ASCIILine": {"type": "keyword"},
    "zope.schema._field.Choice": {"type": "keyword"},
    "zope.schema._field.Datetime": {"type": "date"},
    "zope.schema._field.Tuple": {"type": "keyword"},
    "zope.schema._field.URI": {"type": "text"},
    "zope.schema._field.List": {"type": "keyword"},
}


def _iterate_schema(full_schema):
    for section_name, section in sorted(
        full_schema.items(), key=operator.itemgetter(0)
    ):
        for schema_name, schema in sorted(section.items(), key=operator.itemgetter(0)):
            for field in sorted(schema, key=operator.itemgetter("name")):
                yield section_name, schema_name, field["name"], field["field"]


def create_or_update_mapping(full_schema, index_name):
    es = get_ingest_client()
    if es is None:
        logger.warning("No ElasticSearch client available.")
        return

    # get current mapping
    if es.indices.exists(index_name):
        mapping = es.indices.get_mapping(index=index_name)
        if 'properties' not in mapping[index_name]["mappings"]:
            mapping[index_name]["mappings"]["properties"] = {}
    else:
        # ftr: here is the basic structure of a mapping
        mapping = {index_name: {"mappings": {"properties": {}}}}

    # process mapping
    changed = False
    for section_name, schema_name, field_name, field_type in _iterate_schema(
        full_schema
    ):
        logger.info(str([section_name, field_name, field_type]))
        target_type = FIELDMAP.get(field_type, None)
        if target_type is None:
            logger.warning("{0} field type not in map, ignore.".format(field_type))
            continue
        # full_field_name = "{0}.{1}".format(section_name, field_name)
        if field_name in mapping:
            # todo: check if its the same as before!
            pass
        changed = True
        mapping[index_name]["mappings"]["properties"][field_name] = target_type
    if not changed:
        return
    logger.info(repr(mapping))

    if not es.indices.exists(index_name):
        # if disk is full (dev) this helps. see https://bit.ly/2q1Jzdd
        mapping[index_name]['settings']['blocks']["read_only_allow_delete"] = False
        es.indices.create(index_name, body=mapping[index_name])
    else:
        es.indices.put_mapping(index=index_name, body=mapping)
