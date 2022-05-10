# -*- coding: utf-8 -*-
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
    assert "rid" not in root["@components"]


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
