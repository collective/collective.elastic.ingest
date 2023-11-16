from .. import OPENSEARCH
from ..analysis import update_analysis
from ..client import get_client
from ..logging import logger
from ..mapping import create_or_update_mapping
from ..mapping import expanded_processors
from ..mapping import EXPANSION_FIELDS
from ..mapping import get_field_map
from ..mapping import iterate_schema
from ..postprocessing import postprocess
from ..preprocessing import preprocess
from .blocks import enrichWithBlocksPlainText
from .rid import enrichWithRid
from .section import enrichWithSection
from .security import enrichWithSecurityInfo
from .vocabularyfields import stripVocabularyTermTitles
from pprint import pformat


STATES = {"pipelines_created": False}
PIPELINE_PREFIX = "attachment_ingest"


def _es_pipeline_name(index_name):
    return "{}_{}".format(PIPELINE_PREFIX, index_name)


def setup_ingest_pipelines(full_schema, index_name):
    logger.debug("setup ingest piplines")
    client = get_client()
    pipeline_name = _es_pipeline_name(index_name)
    pipelines = {
        "description": "Extract Plone Binary attachment information",
        "processors": [],
    }
    for section_name, schema_name, field in iterate_schema(full_schema):
        fqfieldname = "/".join([section_name, schema_name, field["name"]])
        fieldmap = get_field_map()
        definition = fieldmap.get(fqfieldname, fieldmap.get(field["field"], None))
        if not definition or "pipeline" not in definition:
            continue
        source = definition["pipeline"]["source"].format(name=field["name"])
        target = definition["pipeline"]["target"].format(name=field["name"])
        pipelines["processors"] += expanded_processors(
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
    """Preprocess content and schema."""

    logger.debug(f"Process content: {pformat(content)}")

    enrichWithSecurityInfo(content)
    enrichWithRid(content)
    enrichWithSection(content)
    enrichWithBlocksPlainText(content)
    stripVocabularyTermTitles(content)
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
