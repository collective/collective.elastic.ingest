# -*- coding: utf-8 -*-
from collections import OrderedDict


PREPROCESSORS = OrderedDict()


def add_additional_field(full_schema, section_name, definition):
    """helper to add additional fields to a full_schema as fetched from Plone
    """
    if "additional" not in full_schema:
        full_schema["additional"] = {}
    if section_name not in full_schema["additional"]:
        full_schema["additional"][section_name] = []
    full_schema["additional"][section_name].append(definition)


def _rid_leverage(content, full_schema, key):
    """take catalog_rif out of @components to the top-level of content
    """
    content["rid"] = content["@components"]["catalog_rid"]
    definition = {"name": "rid", "field": "zope.schema._bootstrapfields.Int"}
    add_additional_field(full_schema, "preprocessed", definition)


PREPROCESSORS["rid_leverage"] = _rid_leverage


# removals
KEYS_TO_REMOVE = ["items", "items_total", "parent", "@components"]


def _remove_entry(content, full_schema, key):
    """remove unused entry
    """
    del content[key]


PREPROCESSORS["@components"] = _remove_entry
PREPROCESSORS["@id"] = _remove_entry
PREPROCESSORS["items"] = _remove_entry
PREPROCESSORS["items_total"] = _remove_entry
PREPROCESSORS["parent"] = _remove_entry
PREPROCESSORS["version"] = _remove_entry
PREPROCESSORS["versioning_enabled"] = _remove_entry


def extract_binary(content, key):
    """
    """
    pass


PREPROCESSORS["binary"] = extract_binary


def preprocess(content, full_schema):
    """run full preprocessing pipeline on content and schema
    """
    for key, preprocessor in PREPROCESSORS.items():
        preprocessor(content, full_schema, key)
