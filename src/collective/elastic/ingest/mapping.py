# -*- coding: utf-8 -*-
from collective.elastic.ingest.elastic import get_ingest_client

import logging
import operator


logger = logging.getLogger(__name__)

ATTACHMENT_DEFINITION_FULL = {
    "type": "nested",
    "properties": {
        "author": {"type": "text"},
        "content": {"type": "text"},
        "content_length": {"type": "long"},
        "content_type": {"type": "keyword"},
        "date": {"type": "date"},
        "keywords": {"type": "keyword"},
        "language": {"type": "keyword"},
        "name": {"type": "text"},
        "title": {"type": "text"},
    },
}
ATTACHMENT_PROCESSORS_DEFAULT = [
    # see https://www.elastic.co/guide/en/elasticsearch/plugins/master/using-ingest-attachment.html  # noqa
    {
        "attachment": {
            "field": "{source}",
            "target_field": "{target}",
            "ignore_missing": True,
        }
    },
    # https://stackoverflow.com/questions/46465523/how-disable-base64-storing-for-ingest-attachment-elasticsearch-plugin # noqa
    {"remove": {"field": "{source}", "ignore_missing": True}},
]

RELATION_DEFINITION_DEFAULT = {
    "type": "nested",
    "properties": {
        "@id": {"type": "keyword"},
        "@type": {"type": "keyword"},
        "description": {"type": "text"},
        "review_state": {"type": "keyword"},
        "title": {"type": "text"},
    },
}

# the fieldmap maps schema fields to elasticseach fields
# key can be
# 1. a dotted name of a schema field class
# 2. the "fully qualified fieldname" from "section_name/schema_name/field_name"
#    example: types/Image/image or behaviors/plone.collection/query
FIELDMAP = {
    "plone.app.textfield.RichText": {
        "pipeline": {
            "source": "{name}__data",
            "target": "{name}__extracted",
            "processors": ATTACHMENT_PROCESSORS_DEFAULT,
            "type": ATTACHMENT_DEFINITION_FULL,
            "expansion": {"method": "field", "field": "data"},
        },
        "definition": {
            "type": "nested",
            "properties": {
                "data": {"type": "text"},
                "content-type": {"type": "keyword"},
                "encoding": {"type": "keyword"},
            },
        },
    },
    "plone.namedfile.field.NamedBlobFile": {
        "pipeline": {
            "source": "{name}__data",
            "target": "{name}__extracted",
            "processors": ATTACHMENT_PROCESSORS_DEFAULT,
            "type": ATTACHMENT_DEFINITION_FULL,
            "expansion": {"method": "fetch", "field": "download"},
        },
        "definition": {
            "type": "nested",
            "properties": {
                "content-type": {"type": "keyword"},
                "download": {"type": "text"},
                "filename": {"type": "text"},
                "size": {"type": "long"},
            },
        },
    },
    "plone.namedfile.field.NamedBlobImage": {
        "pipeline": {
            "source": "{name}__data",
            "target": "{name}__extracted",
            "processors": ATTACHMENT_PROCESSORS_DEFAULT,
            "type": ATTACHMENT_DEFINITION_FULL,
            "expansion": {"method": "fetch", "field": "download"},
        },
        "definition": {
            "type": "nested",
            "properties": {
                "content-type": {"type": "keyword"},
                "download": {"type": "text"},
                "filename": {"type": "text"},
                "size": {"type": "long"},
                "height": {"type": "long"},
                "width": {"type": "long"},
                "scales": {
                    "type": "nested",
                    "properties": {
                        "download": {"type": "text"},
                        "height": {"type": "long"},
                        "width": {"type": "long"},
                    },
                },
            },
        },
    },
    "plone.schema.jsonfield.JSONField": {"type": "text"},
    "z3c.relationfield.schema.RelationList": RELATION_DEFINITION_DEFAULT,
    "z3c.relationfield.schema.RelationChoice": RELATION_DEFINITION_DEFAULT,
    "zope.schema._bootstrapfields.Bool": {"type": "boolean"},
    "zope.schema._bootstrapfields.Int": {"type": "long"},
    "zope.schema._bootstrapfields.Text": {"type": "text"},
    "zope.schema._bootstrapfields.TextLine": {"type": "text"},
    "zope.schema._field.ASCIILine": {"type": "keyword"},
    "zope.schema._field.Choice": {
        "type": "nested",
        "properties": {"token": "keyword", "title": "Text"},
    },
    "zope.schema._field.Datetime": {"type": "date"},
    "zope.schema._field.Dict": {"type": "object"},
    "zope.schema._field.List": {
        "detection": {"default": {"type": "keyword"}, "method": "replace"}
    },
    "zope.schema._field.Tuple": {"type": "keyword"},
    "zope.schema._field.URI": {"type": "text"},
}

# to be filled as cache and renewed on create_or_update_mapping
EXPANSION_FIELDS = {}

STATE = {"initial": True}

DETECTOR_METHODS = {}


def iterate_schema(full_schema):
    for section_name, section in sorted(
        full_schema.items(), key=operator.itemgetter(0)
    ):
        for schema_name, schema in sorted(section.items(), key=operator.itemgetter(0)):
            for field in sorted(schema, key=operator.itemgetter("name")):
                yield section_name, schema_name, field


def _expand_dict(mapping, **kw):
    record = {}
    for key, value in mapping.items():
        if isinstance(value, str):
            value = value.format(**kw)
        elif isinstance(value, dict):
            value = _expand_dict(value, **kw)
        record[key] = value
    return record


def expanded_processors(processors, source, target):
    result = []
    for processor in processors:
        result.append(_expand_dict(processor, source=source, target=target))
    return result


def map_field(field, properties, fqfieldname, seen):
    definition = FIELDMAP.get(fqfieldname, FIELDMAP.get(field["field"], None))
    if definition is None:
        logger.warning(
            "'{0}' field type nor '{1}' FQFN not in map, ignore.".format(
                field["field"], fqfieldname
            )
        )
        return
    seen.add(field["name"])
    logger.info("Map {0} to {1}".format(field["name"], definition))
    if "type" in definition:
        # simple defintion
        properties[field["name"]] = definition
        return
    # complex definition
    if "definition" in definition:
        # direct definition
        properties[field["name"]] = definition["definition"]
    if "detection" in definition:
        DETECTOR_METHODS[definition["detection"]["method"]](
            field, properties, definition, fqfieldname, seen
        )
    if "pipeline" in definition:
        # ingest through pipeline, store result
        pipeline = definition["pipeline"]
        source = pipeline["source"].format(name=field["name"])
        target = pipeline["target"].format(name=field["name"])
        properties[target] = pipeline["type"]

        # memorize this field as expansion field for later use in post_processors
        EXPANSION_FIELDS[field["name"]] = dict(pipeline["expansion"], source=source)


def _replacement_detector(field, properties, definition, fqfieldname, seen):
    replacement = field.get("value_type", None)
    if replacement is None:
        properties[field["name"]] = definition["detection"]["default"]
        return
    replacement["name"] = field["name"]
    map_field(replacement, properties, fqfieldname, seen)


DETECTOR_METHODS["replace"] = _replacement_detector


def create_or_update_mapping(full_schema, index_name):
    es = get_ingest_client()
    if es is None:
        logger.warning("No ElasticSearch client available.")
        return

    # get current mapping
    index_exists = es.indices.exists(index_name)
    if index_exists:
        mapping = es.indices.get_mapping(index=index_name)
        if "properties" not in mapping[index_name]["mappings"]:
            mapping[index_name]["mappings"]["properties"] = {}
    else:
        # ftr: here is the basic structure of a mapping
        mapping = {index_name: {"mappings": {"properties": {}}, "settings": {}}}
    # process mapping
    properties = mapping[index_name]["mappings"]["properties"]
    seen = set()
    for section_name, schema_name, field in iterate_schema(full_schema):
        # try "section_name/schema_name/field[name]/type)"
        value_type = field["field"]
        fqfieldname = "/".join([section_name, schema_name, field["name"]])
        if field["name"] in seen:
            logger.info(
                "Skip dup field definition {0} with {1}. Already defined: {2}".format(
                    fqfieldname, value_type, properties[field["name"]]
                )
            )
            continue
        map_field(field, properties, fqfieldname, seen)

    STATE["initial"] = False

    # if disk is full (dev) this helps. see https://bit.ly/2q1Jzdd
    from pprint import pformat

    logger.warn(pformat(mapping))
    if index_exists:
        # xxx: here a check if the schema is different from the original could be fine
        es.indices.put_mapping(index=index_name, body=mapping[index_name]["mappings"])
    else:
        # from celery.contrib import rdb; rdb.set_trace()
        mapping[index_name].setdefault(
            "settings", {"blocks": {"read_only_allow_delete": False}}
        )
        es.indices.create(index_name, body=mapping[index_name])
