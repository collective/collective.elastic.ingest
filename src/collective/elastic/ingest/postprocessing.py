# -*- coding: utf-8 -*-
from collections import OrderedDict
from collective.elastic.ingest.plone import fetch_binary

import base64

POSTPROCESSORS: OrderedDict = OrderedDict()


def _extract_binary(content: dict, info: dict, key: str):
    """
    """
    for field_name, config in info["expansion_fields"].items():
        if field_name not in content:
            continue
        if config["method"] == "fetch":
            data = fetch_binary(content[field_name][config["field"]])
        elif config["method"] == "field":
            data = content[field_name][config["field"]]
        content[config["source"]] = base64.b64encode(data).decode("utf8")


POSTPROCESSORS["binary"] = _extract_binary


def postprocess(content: dict, info: dict):
    """run full postprocessing pipeline on content and schema
    """
    for key, postprocessor in POSTPROCESSORS.items():
        postprocessor(content, info, key)
