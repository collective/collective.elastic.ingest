# -*- coding: utf-8 -*-
from collective.elastic.ingest import preprocessing

# ------------------------------------------------------------------------------
# helper


def test__add_additional_field__main_section_empty():
    full_schema = {}
    preprocessing.add_additional_field(full_schema, "test", {1: 2})
    assert full_schema == {"additional": {"test": [{1: 2}]}}


def test__add_additional_field__main_section_exists():
    full_schema = {"additional": {}}
    preprocessing.add_additional_field(full_schema, "test", {1: 2})
    assert full_schema == {"additional": {"test": [{1: 2}]}}


def test__add_additional_field__main_and_sub_section_exists():
    full_schema = {"additional": {"test": []}}
    preprocessing.add_additional_field(full_schema, "test", {1: 2})
    assert full_schema == {"additional": {"test": [{1: 2}]}}


# ------------------------------------------------------------------------------
# preprocessors


def test__rid_leverage():
    content = {"@components": {"catalog_rid": 1}}
    full_schema = {}
    preprocessing._rid_leverage(content, full_schema, "test")
    assert content == {"@components": {"catalog_rid": 1}, "rid": 1}
    assert full_schema == {
        "additional": {
            "preprocessed": [
                {"field": "zope.schema._bootstrapfields.Int", "name": "rid"}
            ]
        }
    }


# ------------------------------------------------------------------------------
# full processor
