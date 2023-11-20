from .. import OPENSEARCH
from ..analysis import update_analysis
from ..client import get_client
from ..logging import logger
from ..mapping import create_or_update_mapping
from ..mapping import EXPANSION_FIELDS
from ..mapping import get_field_map
from ..mapping import iterate_schema
from ..postprocessing import postprocess
from ..preprocessing import preprocess
from .section import enrichWithSection
from .vocabularyfields import stripVocabularyTermTitles
from pprint import pformat


STATES = {"pipelines_created": False}
PIPELINE_PREFIX = "attachment_ingest"


def _es_pipeline_name(index_name):
    """Return the name of the ingest pipeline for the given index."""
    return "{}_{}".format(PIPELINE_PREFIX, index_name)


def _expand_dict(mapping, **kw):
    """Recursivly expand a dictionary with keyword arguments."""
    record = {}
    for key, value in mapping.items():
        if isinstance(value, str):
            value = value.format(**kw)
        elif isinstance(value, dict):
            value = _expand_dict(value, **kw)
        record[key] = value
    return record


def _expanded_processors(processors, source, target):
    """Expand a list of processors with source and target."""
    result = []
    for processor in processors:
        result.append(_expand_dict(processor, source=source, target=target))
    return result


def setup_ingest_pipelines(full_schema, index_name):
    """Setup ingest pipelines for the given index based on the schema."""
    logger.debug("setup ingest piplines")
    client = get_client()
    pipeline_name = _es_pipeline_name(index_name)
    pipelines = {
        "description": "Extract Plone Binary attachment information",
        "processors": [],
    }
    fieldmap = get_field_map()
    for section_name, schema_name, field in iterate_schema(full_schema):
        fqfieldname = "/".join([section_name, schema_name, field["name"]])
        definition = fieldmap.get(fqfieldname, fieldmap.get(field["field"], None))
        if not definition or "pipeline" not in definition:
            continue
        source = definition["pipeline"]["source"].format(name=field["name"])
        target = definition["pipeline"]["target"].format(name=field["name"])
        pipelines["processors"] += _expanded_processors(
            definition["pipeline"]["processors"], source, target
        )
    if pipelines["processors"]:
        logger.info(f"update ingest pipelines {pipeline_name}")
        logger.debug(f"pipeline definitions:\n{pipelines}")
        if OPENSEARCH:
            client.ingest.put_pipeline(id=pipeline_name, body=pipelines)
        else:
            client.ingest.put_pipeline(
                id=pipeline_name, processors=pipelines["processors"]
            )
    else:
        logger.info(f"delete ingest pipelines {pipeline_name}")
        client.ingest.delete_pipeline(pipeline_name)


def ingest(content, full_schema, index_name):
    """Process content and schema.

    This brings it together: Preprocess, create a mapping (and index/pipelines if not exists yet),
    then postprocess and finally index the content.
    """

    logger.debug(f"Process content: {pformat(content)}")

    # special preprocessing logic for section and vocabulary fields
    # TODO: refactor as special preprocessing
    enrichWithSection(content)
    stripVocabularyTermTitles(content)

    # generic preprocessing accrording to rule in preprocessings.json
    preprocess(content, full_schema)

    if full_schema:
        # first update_analysis, then create_or_update_mapping:
        # mapping can use analyzers from analysis.json
        update_analysis(index_name)
        create_or_update_mapping(full_schema, index_name)
        if not STATES["pipelines_created"]:
            setup_ingest_pipelines(full_schema, index_name)
            STATES["pipelines_created"] = True
    info = {"expansion_fields": EXPANSION_FIELDS}
    postprocess(content, info)

    logger.info(f"Index content: {pformat(content)}")
    client = get_client()
    kwargs = dict(
        index=index_name,
        id=content["UID"],
        pipeline=_es_pipeline_name(index_name),
        body=content,
    )
    client.index(**kwargs)
