def enrichWithSecurityInfo(content):
    content["allowedRolesAndUsers"] = content["@components"]["collectiveelastic"][
        "allowedRolesAndUsers"
    ]
    return content
