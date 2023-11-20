from . import OPENSEARCH
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
DEFAULT_INDEX_SETTINGS = {
    # xxx: number should be made configurable
    "index.mapping.nested_fields.limit": 100,
    # xxx: to be removed or at least made configurable by env var
    # if disk is full (dev) this helps. see https://bit.ly/2q1Jzdd
    "index.blocks.read_only_allow_delete": False,
}

DETECTOR_METHODS: dict[str, typing.Callable] = {}


def get_field_map() -> dict:
    """The field map from file passed as filename in an env var.

    To not load 1000s of times, this is cached.
    """
    if STATE["fieldmap"] == {}:
        _mappings_file = os.environ.get("MAPPINGS_FILE", None)
        if not _mappings_file:
            raise ValueError("No mappings file configured.")
        with open(_mappings_file) as fp:
            STATE["fieldmap"] = json.load(fp)
    assert isinstance(STATE["fieldmap"], dict)
    return STATE["fieldmap"]


def iterate_schema(
    full_schema: dict[str, dict[str, dict[str, dict]]],
) -> typing.Generator[tuple, None, None]:
    """Iterate over the 3 Levels of the schema and flattend yield field definitions.

    The full_schema is the dict as received from Plone "@cesp" endpoint.
    The endpoint is defined in collective.elastic.plone.

    The yielded tuple containes the section_name, schema_name and field definition.
    """
    for section_name, section in sorted(
        full_schema.items(), key=operator.itemgetter(0)
    ):
        for schema_name, schema in sorted(section.items(), key=operator.itemgetter(0)):
            logger.debug(f"Schema: {section_name}/{schema_name}\n{schema}")
            for field in sorted(schema, key=operator.itemgetter("name")):
                yield section_name, schema_name, field


def map_field(field, properties, fqfieldname, seen):
    """Map a field to a definition and add it to the properties."""
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
    """Remember expansion fields for later use in post_processors.

    This are fields where content need to be added in a postprocessing step,
    i.e. images or files to be fetched from Plone, because the binaries are
    not part of the inital information.
    """
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
    # since we replace here, a new expansion field could be needed
    update_expansion_fields(field, fqfieldname)
    map_field(replacement, properties, fqfieldname, seen)


DETECTOR_METHODS["replace"] = _replacement_detector


def create_or_update_mapping(full_schema, index_name: str) -> None:
    """Create or update the mapping for the given index.

    Based on the full_schema as provided by the "@cesp" endpoint,
    enriched by the preprocessings.

    Based on the MAPPINGS_FILE env var JSON file.

    It globally collects fields for later expansion in postprocessing.

    Finaly it initially creates the index (also index settings are set)
    or updates the mapping for the given index.
    """
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
            "mappings": {
                "properties": {},
            },
            "settings": DEFAULT_INDEX_SETTINGS,
        }
    # process mapping
    properties = mapping["mappings"]["properties"]
    seen: set[str] = set()
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
    # TODO: handle this with preprocessings.json
    map_field(
        dict(name="blocks_plaintext", field="blocks_plaintext"),
        properties,
        "blocks_plaintext",
        seen,
    )

    STATE["initial"] = False
    if index_exists:
        if json.dumps(original_mapping["mappings"], sort_keys=True) == json.dumps(
            mapping["mappings"], sort_keys=True
        ):
            logger.debug("No update necessary. Mapping is unchanged.")
            return

        logger.info("Update mapping.")
        logger.debug(
            "Mapping is:\n{}".format(
                json.dumps(mapping["mappings"], sort_keys=True, indent=2)
            )
        )
        if OPENSEARCH:
            client.indices.put_mapping(
                index=[index_name],
                body=mapping,
            )
        else:
            client.indices.put_mapping(
                index=index_name,
                properties=mapping["mappings"]["properties"],
            )
        return

    logger.info("Create index with mapping.")
    logger.debug(f"mapping is:\n{json.dumps(mapping, sort_keys=True, indent=2)}")
    if OPENSEARCH:
        # both, settings and mappings, at once
        client.indices.create(index=index_name, body=mapping)
    else:
        # first create index, then settings, then mappings
        client.indices.create(index=index_name)
        client.indices.put_settings(
            settings=mapping["settings"],
            index=index_name,
        )
        client.indices.put_mapping(
            index=index_name,
            properties=mapping["mappings"]["properties"],
        )
