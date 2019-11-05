# -*- coding: utf-8 -*-
from collective.elastic.ingest.elastic import get_ingest_client
from elasticsearch.exceptions import NotFoundError

import logging
import operator
import six


logger = logging.getLogger(__name__)

# the fieldmap maps schema fields to elasticseach fields
# key can be
# 1. a dotted name of a schema field class
# 2. the "fully qualified fieldname" from "section_name/schema_name/field_name"
#    example: types/Image/image or behaviors/plone.collection/query
FIELDMAP = {
    "plone.app.textfield.RichText": {
        "processor": {
            # see https://www.elastic.co/guide/en/elasticsearch/plugins/master/using-ingest-attachment.html  # noqa
            "attachment": {
                "field": "{name}",
                "target_field": "{name}__extracted",
                "ignore_missing": True,
            },
        },
        "type": "text",
    },
    "plone.namedfile.field.NamedBlobFile": {
        "processor": {
            "attachment": {
                "field": "{name}",
                "target_field": "{name}__extracted",
                "ignore_missing": True,
            },
        },
        "type": "text",
    },
    "plone.namedfile.field.NamedBlobImage": {
        "processor": {
            "attachment": {
                "field": "{name}",
                "target_field": "{name}__extracted",
                "ignore_missing": True,
            },
        },
        "type": "text",
    },
    "plone.schema.jsonfield.JSONField": {"type": "text"},
    "zope.schema._bootstrapfields.Bool": {"type": "boolean"},
    "zope.schema._bootstrapfields.Int": {"type": "long"},
    "zope.schema._bootstrapfields.Text": {"type": "text"},
    "zope.schema._bootstrapfields.TextLine": {"type": "text"},
    "zope.schema._field.ASCIILine": {"type": "keyword"},
    "zope.schema._field.Choice": {"type": "keyword"},
    "zope.schema._field.Datetime": {"type": "date"},
    "zope.schema._field.Dict": {"type": "object"},
    "zope.schema._field.List": {"type": "keyword"},
    "zope.schema._field.Tuple": {"type": "keyword"},
    "zope.schema._field.URI": {"type": "text"},
}

PIPELINE_PREFIX = "attachment_ingest"


def _es_pipeline_name(index_name):
    return "{0}_{1}".format(PIPELINE_PREFIX, index_name)


def _iterate_schema(full_schema):
    for section_name, section in sorted(
        full_schema.items(), key=operator.itemgetter(0)
    ):
        for schema_name, schema in sorted(section.items(), key=operator.itemgetter(0)):
            for field in sorted(schema, key=operator.itemgetter("name")):
                yield section_name, schema_name, field


def setup_ingest_pipelines(full_schema, index_name):
    es = get_ingest_client()
    pipeline_name = _es_pipeline_name(index_name)
    do_create = False
    try:
        es.ingest.get_pipeline(pipeline_name)
    except NotFoundError:
        do_create = True
    if not do_create:
        return
    pipelines = {
        'description': 'Extract Plone Binary attachment information',
        'processors': []
    }
    for section_name, schema_name, field in _iterate_schema(full_schema):
        value_type = field.get("value_type", field["field"])
        fqfieldname = "/".join([section_name, schema_name, field["name"]])
        definition = FIELDMAP.get(fqfieldname, FIELDMAP.get(value_type, None))
        if not definition or "processor" not in definition:
            continue
        attachment = {}
        pipelines['processors'].append({'attachment': attachment})
        for key, value in definition["processor"]["attachment"].items():
            if isinstance(value, six.string_types):
                attachment[key] = value.format(name=field["name"])
            else:
                attachment[key] = value
    logger.warning(str(pipelines))
    if pipelines['processors']:
        es.ingest.put_pipeline(pipeline_name, pipelines)
    else:
        es.ingest.delete_pipeline(pipeline_name)


def create_or_update_mapping(full_schema, index_name):
    es = get_ingest_client()
    if es is None:
        logger.warning("No ElasticSearch client available.")
        return

    # get current mapping
    if es.indices.exists(index_name):
        mapping = es.indices.get_mapping(index=index_name)
        if "properties" not in mapping[index_name]["mappings"]:
            mapping[index_name]["mappings"]["properties"] = {}
    else:
        # ftr: here is the basic structure of a mapping
        mapping = {index_name: {"mappings": {"properties": {}}, "settings": {}}}
    logger.info(mapping)
    # process mapping
    changed = False
    for section_name, schema_name, field in _iterate_schema(full_schema):
        if field["name"] in mapping[index_name]["mappings"]["properties"]:
            # todo: check if its the same as before!
            logger.info("skip existing definition for field {0}".format(field["name"]))
            continue
        logger.info("process " + str([section_name, field]))
        # try "section_name/schema_name/field[name]/type)"
        value_type = field.get("value_type", field["field"])
        fqfieldname = "/".join([section_name, schema_name, field["name"]])
        definition = FIELDMAP.get(fqfieldname, FIELDMAP.get(value_type, None))
        if definition is None:
            logger.warning(
                "'{0}' field type nor '{1}' FQFN not in map, ignore.".format(
                    value_type, fqfieldname
                )
            )
            continue
        # full_field['name'] = "{0}.{1}".format(section_name, field['name'])
        changed = True
        if "processor" in definition:
            # ingest through pipeline, store result
            mapping[index_name]["mappings"]["properties"][field["name"]] = {
                "type": "nested",
                "properties": {
                    "content": {"type": definition['type']},
                    "content_length": {"type": "long"},
                    "content_type": {"type": "keyword"},
                    "language": {"type": "keyword"},
                },
            }
        elif "type" in definition:
            mapping[index_name]["mappings"]["properties"][field["name"]] = definition
        if not ("type" in definition or "processor" in definition):
            logger.warning(
                "'{0}' field type '{1}' FQFN definition in map {2} invalid,"
                "ignore.".format(value_type, fqfieldname, definition)
            )

    if not changed:
        return
    logger.info(repr(mapping))

    if not es.indices.exists(index_name):
        # if disk is full (dev) this helps. see https://bit.ly/2q1Jzdd
        mapping[index_name].setdefault(
            "settings", {"blocks": {"read_only_allow_delete": False}}
        )
        # from celery.contrib import rdb; rdb.set_trace()
        es.indices.create(index_name, body=mapping[index_name])
    else:
        es.indices.put_mapping(index=index_name, body=mapping)
