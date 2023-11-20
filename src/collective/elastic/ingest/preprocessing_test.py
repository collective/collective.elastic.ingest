from . import preprocessing

import pytest


# ------------------------------------------------------------------------------
# helper


def test_find_last_container_in_path_flat():
    root = {"corona": "lockdown"}
    container, key = preprocessing._find_last_container_in_path(root, ["corona"])
    assert container is root
    assert key == "corona"


def test_find_last_container_in_path_nested():
    date_container = {"date": "2020-03-16"}
    root = {"corona": {"lockdown": date_container}}
    container, key = preprocessing._find_last_container_in_path(
        root, ["corona", "lockdown", "date"]
    )
    assert container is date_container
    assert key == "date"


# ------------------------------------------------------------------------------
# actions


def test_action_rewrite():
    ridvalue = 1234567890
    root = {
        "@components": {
            "rid": ridvalue,
        }
    }
    config = {"source": "@components/rid", "target": "rid"}
    preprocessing.action_rewrite(root, {}, config)
    assert "rid" in root
    assert root["rid"] == ridvalue


def test_action_rewrite_non_existing():
    root = {"@components": {}}
    config = {"source": "@components/rid", "target": "rid"}
    preprocessing.action_rewrite(root, {}, config)
    assert "rid" not in root


def test_action_rewrite_non_existing_forced():
    root = {"@components": {}}
    config = {
        "source": "@components/rid",
        "target": "rid",
        "enforce": True,
    }
    with pytest.raises(ValueError):
        preprocessing.action_rewrite(root, {}, config)


def test_action_field_remove():
    full_schema = {
        "behaviors": {
            "plone.basic": [
                {"field": "zope.schema._bootstrapfields.TextLine", "name": "title"},
                {"field": "zope.schema._bootstrapfields.Text", "name": "description"},
            ]
        }
    }
    config = {
        "section": "behaviors",
        "name": "plone.basic",
        "field": "title",
    }
    root = {
        "foo": "bar",
        "title": "Foo",
    }

    preprocessing.action_field_remove(root, full_schema, config)

    assert root == {"foo": "bar"}
    assert len(full_schema["behaviors"]["plone.basic"]) == 1


def test_action_full_remove():
    full_schema = {
        "behaviors": {
            "plone.basic": [
                {"field": "zope.schema._bootstrapfields.TextLine", "name": "title"},
                {"field": "zope.schema._bootstrapfields.Text", "name": "description"},
            ],
            "plone.categorization": [
                {
                    "field": "zope.schema._field.Tuple",
                    "name": "subjects",
                    "value_type": {"field": "zope.schema._bootstrapfields.TextLine"},
                },
                {"field": "zope.schema._field.Choice", "name": "language"},
            ],
        }
    }
    config = {
        "section": "behaviors",
        "name": "plone.categorization",
    }
    root = {
        "title": "Foo",
        "description": "Bar",
        "subjects": ["Foo", "Bar"],
        "language": "de",
        "baz": "Baaz",
    }

    preprocessing.action_full_remove(root, full_schema, config)

    assert root == {"baz": "Baaz", "description": "Bar", "title": "Foo"}
    assert "plone.categorization" not in full_schema["behaviors"]
