from .logging import logger

import json
import os


_preprocessings_file = os.environ.get(
    "PREPROCESSINGS_FILE",
    os.path.join(os.path.dirname(__file__), "preprocessings.json"),
)

with open(_preprocessings_file) as fp:
    PREPROCESSOR_CONFIGS = json.load(fp)

# MATCHERS
MATCHING_FUNCTIONS = {}


def match_always(content, full_schema, config):
    return True


MATCHING_FUNCTIONS["always"] = match_always


def match_content_exists(content, full_schema, config):
    path = config["path"].split("/")
    current = content
    for el in path:
        current = current.get(el, None)
        if current is None:
            return False
    return True


MATCHING_FUNCTIONS["content_exists"] = match_content_exists


# ACTIONS

ACTION_FUNCTIONS = {}


def action_additional_schema(content, full_schema, config):
    """add additional fields to a full_schema as fetched from Plone"""
    if full_schema is None:
        # case: in subsequent calls there is no need to modify schema b/c of caching
        return
    additional = full_schema.setdefault("additional", {})
    preprocessed = additional.setdefault("preprocessed", [])
    preprocessed.append(config)


ACTION_FUNCTIONS["additional_schema"] = action_additional_schema


def _find_last_container_in_path(root, path):
    if len(path) == 1:
        return root, path[0]
    if path[0] not in root:
        return None, None
    return _find_last_container_in_path(root[path[0]], path[1:])


def action_rewrite(content, full_schema, config):
    enforce = config.get("enforce", False)
    source_container, source_key = _find_last_container_in_path(
        content, config["source"].split("/")
    )
    if source_container is None:
        if enforce:
            raise ValueError(
                "Source container {} not in content.".format(config["source"])
            )
        return
    target_container, target_key = _find_last_container_in_path(
        content, config["target"].split("/")
    )
    if target_container is None:
        if enforce:
            raise ValueError(
                "Target container {} not in content.".format(config["source"])
            )
        return
    if source_key not in source_container:
        if enforce:
            raise ValueError("Source {} not in content.".format(config["source"]))
        return
    target_container[target_key] = source_container[source_key]
    del source_container[source_key]


ACTION_FUNCTIONS["rewrite"] = action_rewrite


def action_remove(content, full_schema, config):
    """remove unused entry"""
    target, target_key = _find_last_container_in_path(
        content,
        config["target"].split("/"),
    )
    if target and target_key in target:
        del target[target_key]


ACTION_FUNCTIONS["remove"] = action_remove


def action_field_remove(content, full_schema, config):
    """remove full field from content and schema."""
    if config["field"] in content:
        del content[config["field"]]
    if not full_schema:
        # cached schema, not passed, no need to process
        return
    section = full_schema[config["section"]]
    fields = section[config["name"]]
    index = [f["name"] for f in fields].index(config["field"])
    del fields[index]


ACTION_FUNCTIONS["field_remove"] = action_field_remove


def action_full_remove(content, full_schema, config):
    """remove full behavior or types fields."""
    if full_schema:
        section = full_schema[config["section"]]
        # we need to cache the fields, because in subsequent calls there is no schema provided
        fields = section.get(config["name"], [])
        if fields:
            del section[config["name"]]
        config["__fields"] = fields
    else:
        fields = config["__fields"]
    for field in fields:
        if field["name"] in content:
            del content[field["name"]]


ACTION_FUNCTIONS["full_remove"] = action_full_remove


def action_empty_removal(content, full_schema, key):
    """remove empty fields"""
    to_remove = set()
    for name, value in content.items():
        if value is None or value == "" or value == [] or value == {}:
            to_remove.add(name)
    for name in to_remove:
        del content[name]


ACTION_FUNCTIONS["remove_empty"] = action_empty_removal


def action_strip_vocabulary_term_titles(content, full_schema, config):
    """If field with vocabulary: Convert field value to token or list of tokens."""
    for fieldname, field in content.items():
        if isinstance(field, dict) and set(field.keys()) == {"title", "token"}:
            content[fieldname] = field["token"]
        elif (
            isinstance(field, list)
            and len(field) > 0
            and isinstance(field[0], dict)
            and set(field[0].keys()) == {"title", "token"}
        ):
            content[fieldname] = [el["token"] for el in field]


ACTION_FUNCTIONS["strip_vocabulary_term_titles"] = action_strip_vocabulary_term_titles


def action_enrich_with_section(content, fullschema, config):
    """Add section to content.

    TODO: make this take the site root into account and remove this step (see below)

    At the moment this is not very generic.
    It guesses the section based on the path element after the root.

    In fact, this element can be something else, e.g. a language root folder defining a subsite.
    Same is possible with Lineage based subsites and so on.

    A solution would be to add an expansion in c.e.plone to add the site and section to the content and use this information.
    Then this step can be deprecated and later on removed and a rewrite + addtional schema would be enough.
    """
    base = "/".join(
        [
            str(os.environ.get("PLONE_SERVICE")),
            str(os.environ.get("PLONE_PATH")),
        ]
    ).strip("/")
    content_url = content["@id"]
    path = content_url.replace(base, "")
    content["section"] = path.split("/")[1] if len(path.split("/")) > 1 else "__root__"


ACTION_FUNCTIONS["enrich_with_section"] = action_enrich_with_section


def preprocess(content, full_schema):
    """run full preprocessing pipeline on content and schema"""
    for ppcfg in PREPROCESSOR_CONFIGS:
        logger.debug("Preprocessor configuration:\n{}\n".format(ppcfg))
        match = ppcfg.get("match", {"type": "always"})
        matcher = MATCHING_FUNCTIONS[match["type"]]
        if not matcher(content, full_schema, match):
            continue
        action = ACTION_FUNCTIONS[ppcfg["action"]]
        action(content, full_schema, ppcfg.get("configuration", {}))
