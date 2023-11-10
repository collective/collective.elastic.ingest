import os


def enrichWithSection(content):
    base = "/".join(
        [
            str(os.environ.get("PLONE_SERVICE")),
            str(os.environ.get("PLONE_PATH")),
        ]
    ).strip("/")
    content_url = content["@id"]
    path = content_url.replace(base, "")
    content["section"] = path.split("/")[1] if len(path.split("/")) > 1 else "__root__"
    return content
