from ..logging import logger


def stripVocabularyTermTitles(content):
    """If field with vocabulary: Convert field value to token or list of tokens."""
    for fieldname in content.keys():
        logger.debug(f"{fieldname} {content[fieldname]}")
        if type(content[fieldname]) == dict:

            if sorted(list(content[fieldname].keys())) == ["title", "token"]:
                content[fieldname] = content[fieldname]["token"]

        if type(content[fieldname]) == list:
            if (
                len(content[fieldname]) > 0
                and type(content[fieldname][0]) == dict
                and sorted(list(content[fieldname][0].keys())) == ["title", "token"]
            ):
                content[fieldname] = [el["token"] for el in content[fieldname]]
    return content
