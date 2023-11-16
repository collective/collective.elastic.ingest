from .client import get_client
from .logging import logger
from copy import deepcopy

import json
import operator
import os
import pprint
import typing


pp = pprint.PrettyPrinter(indent=4)


# to be filled as cache and renewed on create_or_update_mapping
EXPANSION_FIELDS = {}

STATE = {
    "initial": True,
    "fieldmap": {},
}

DETECTOR_METHODS: dict[str, typing.Callable] = {}


def get_field_map() -> dict:
    if STATE["fieldmap"] == {}:
        _mappings_file = os.environ.get("MAPPINGS_FILE", None)
        if not _mappings_file:
            raise ValueError("No mappings file configured.")
        with open(_mappings_file) as fp:
            STATE["fieldmap"] = json.load(fp)
    assert isinstance(STATE["fieldmap"], dict)
    return STATE["fieldmap"]


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
    fieldmap = get_field_map()
    definition = fieldmap.get(fqfieldname, fieldmap.get(field["field"], None))
    if definition is None:
        logger.warning(
            "Ignore: '{}' field type nor '{}' FQFN in map.".format(
                field["field"], fqfieldname
            )
        )
        return
    seen.add(field["name"])
    logger.debug(f"Map field name {field['name']} to definition {definition}")
    if "type" in definition:
        # simple definition
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
    fieldmap = get_field_map()
    definition = fieldmap.get(fqfieldname, fieldmap.get(field["field"], None))
    if definition is None:
        logger.warning(
            "Ignore: '{}' field type nor '{}' FQFN in map.".format(
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
    client = get_client()
    if client is None:
        logger.warning("No index client available.")
        return

    # get current mapping
    index_exists = client.indices.exists(index=index_name)
    if index_exists:
        original_mapping = client.indices.get_mapping(index=index_name)[index_name]
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
                "{} with {}. Already defined: {}".format(
                    fqfieldname, value_type, properties[field["name"]]
                )
            )
            continue
        if field["name"] in seen:
            logger.debug(
                "Skip dup field definition {} with {}.".format(
                    fqfieldname,
                    value_type,
                )
            )
            continue
        map_field(field, properties, fqfieldname, seen)

    # Mapping for blocks_plaintext (not a schema field, but received from api expansion "collectiveelastic")
    map_field(
        dict(name="blocks_plaintext", field="blocks_plaintext"),
        properties,
        "blocks_plaintext",
        seen,
    )

    STATE["initial"] = False
    if index_exists:
        if json.dumps(original_mapping["mappings"], sort_keys=True) != json.dumps(
            mapping["mappings"], sort_keys=True
        ):
            logger.info("Update mapping.")
            logger.debug(
                "Mapping is:\n{}".format(
                    json.dumps(mapping["mappings"], sort_keys=True, indent=2)
                )
            )
            client.indices.put_mapping(
                index=[index_name],
                body=mapping["mappings"],
            )
        else:
            logger.debug("No update necessary. Mapping is unchanged.")
    else:
        logger.info("Create index with mapping.")
        logger.debug(f"mapping is:\n{json.dumps(mapping, sort_keys=True, indent=2)}")
        client.indices.create(index=index_name, mappings=mapping["mappings"])
