from ..logging import logger

import os


def enrichWithSecurityInfo(content):
    content["allowedRolesAndUsers"] = content["@components"][
        "component_allowedRolesAndUsers"
    ]
    return content
