def enrichWithRid(content):
    if "collectiveelastic" in content["@components"]:
        content["rid"] = content["@components"]["collectiveelastic"]["catalog_rid"]
    # BBB backward compatibility
    elif "catalog_rid" in content["@components"]:
        content["rid"] = content["@components"]["catalog_rid"]
    return content
