# -*- coding: utf-8 -*-
from .elastic import get_ingest_client
from .logging import logger
from copy import deepcopy
from collective.elastic.ingest import ELASTICSEARCH_7

import json
import operator
import os
import pprint


pp = pprint.PrettyPrinter(indent=4)


# to be filled as cache and renewed on create_or_update_mapping
EXPANSION_FIELDS = {}

STATE = {"initial": True}

DETECTOR_METHODS = {}

_mappings_file = os.environ.get(
    "MAPPINGS_FILE", os.path.join(os.path.dirname(__file__), "mappings.json")
)

with open(_mappings_file, mode="r") as fp:
    FIELDMAP = json.load(fp)


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
            "Ignore: '{0}' field type nor '{1}' FQFN in map.".format(
                field["field"], fqfieldname
            )
        )
        return
    seen.add(field["name"])
    logger.debug(f"Map field name {field['name']} to definition {definition}")
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
        target = pipeline["target"].format(name=field["name"])
        properties[target] = pipeline["type"]


def update_expansion_fields(field, fqfieldname):
    definition = FIELDMAP.get(fqfieldname, FIELDMAP.get(field["field"], None))
    if definition is None:
        logger.warning(
            "Ignore: '{0}' field type nor '{1}' FQFN in map.".format(
                field["field"], fqfieldname
            )
        )
        return
    if "pipeline" in definition:
        # ingest through pipeline, store result
        pipeline = definition["pipeline"]
        source = pipeline["source"].format(name=field["name"])

        # memorize this field
        # as expansion field for later use in post_processors
        EXPANSION_FIELDS[field["name"]] = dict(pipeline["expansion"], source=source)


def _replacement_detector(field, properties, definition, fqfieldname, seen):
    replacement = field.get("value_type", None)
    if replacement is None:
        properties[field["name"]] = definition["detection"]["default"]
        return
    replacement["name"] = field["name"]
    update_expansion_fields(
        field, fqfieldname
    )  # TODO Needed here? Was part of map_field.
    map_field(replacement, properties, fqfieldname, seen)


DETECTOR_METHODS["replace"] = _replacement_detector


def create_or_update_mapping(full_schema, index_name):
    es = get_ingest_client()
    if es is None:
        logger.warning("No ElasticSearch client available.")
        return

    # get current mapping
    if ELASTICSEARCH_7:
        index_exists = es.indices.exists(index_name)
    else:
        index_exists = es.indices.exists(index=index_name)
    if index_exists:
        original_mapping = es.indices.get_mapping(index=index_name)[index_name]
        mapping = deepcopy(original_mapping)
        if "properties" not in mapping["mappings"]:
            mapping["mappings"]["properties"] = {}
    else:
        # ftr: here is the basic structure of a mapping
        mapping = {
            "mappings": {"properties": {}},
            "settings": {
                # xxx: number should be made configurable
                "index.mapping.nested_fields.limit": 100,
                # xxx: to be removed or at least made configurable by env var
                # if disk is full (dev) this helps. see https://bit.ly/2q1Jzdd
                "index.blocks.read_only_allow_delete": False,
            },
        }
    # process mapping
    properties = mapping["mappings"]["properties"]
    seen = set()
    for section_name, schema_name, field in iterate_schema(full_schema):
        # try "section_name/schema_name/field[name]/type)"
        value_type = field["field"]
        fqfieldname = "/".join([section_name, schema_name, field["name"]])
        update_expansion_fields(field, fqfieldname)
        if field["name"] in properties:
            logger.debug(
                "Skip existing field definition "
                "{0} with {1}. Already defined: {2}".format(
                    fqfieldname, value_type, properties[field["name"]]
                )
            )
            continue
        if field["name"] in seen:
            logger.debug(
                "Skip dup field definition {0} with {1}.".format(
                    fqfieldname,
                    value_type,
                )
            )
            continue
        map_field(field, properties, fqfieldname, seen)

    STATE["initial"] = False
    if index_exists:
        if json.dumps(original_mapping["mappings"], sort_keys=True) != json.dumps(
            mapping["mappings"], sort_keys=True
        ):
            logger.info("Update mapping.")
            logger.debug(
                "Mapping is:\n{0}".format(
                    json.dumps(mapping["mappings"], sort_keys=True, indent=2)
                )
            )
            if ELASTICSEARCH_7:
                es.indices.put_mapping(index=index_name, body=mapping["mappings"])
            else:
                es.indices.put_mapping(
                    index=[index_name],
                    body=mapping["mappings"],
                )
        else:
            logger.debug("No update necessary. Mapping is unchanged.")
    else:
        # from celery.contrib import rdb; rdb.set_trace()
        logger.info("Create index with mapping.")
        logger.debug(f"mapping is:\n{json.dumps(mapping, sort_keys=True, indent=2)}")
        if ELASTICSEARCH_7:
            es.indices.create(index_name, body=mapping)
        else:
            es.indices.create(index=index_name, mappings=mapping["mappings"])
