# -*- coding: utf-8 -*-
from .plone import fetch_binary
from collections import OrderedDict
from .logging import logger

import base64


POSTPROCESSORS = OrderedDict()


def _extract_binary(content, info, key):
    """ """
    for field_name, config in info["expansion_fields"].items():
        if field_name not in content:
            continue
        if config["method"] == "fetch":
            data = fetch_binary(content[field_name][config["field"]])
        elif config["method"] == "field":
            data = content[field_name][config["field"]].encode("utf8")
        content[config["source"]] = base64.b64encode(data).decode("utf8")


POSTPROCESSORS["binary"] = _extract_binary


def postprocess(content, info):
    """run full postprocessing pipeline on content and schema"""
    logger.debug(f"postprocess with {info}")
    for key, postprocessor in POSTPROCESSORS.items():
        postprocessor(content, info, key)
