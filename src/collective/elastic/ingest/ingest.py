# -*- coding: utf-8 -*-
from .elastic import get_ingest_client
from .logging import logger
from .mapping import create_or_update_mapping
from .mapping import expanded_processors
from .mapping import EXPANSION_FIELDS
from .mapping import FIELDMAP
from .mapping import iterate_schema
from .postprocessing import postprocess
from .preprocessing import preprocess


STATES = {"pipelines_created": False}

PIPELINE_PREFIX = "attachment_ingest"


def _es_pipeline_name(index_name):
    return "{0}_{1}".format(PIPELINE_PREFIX, index_name)


def setup_ingest_pipelines(full_schema, index_name):
    es = get_ingest_client()
    pipeline_name = _es_pipeline_name(index_name)
    pipelines = {
        "description": "Extract Plone Binary attachment information",
        "processors": [],
    }
    for section_name, schema_name, field in iterate_schema(full_schema):
        value_type = field.get("value_type", field["field"])
        fqfieldname = "/".join([section_name, schema_name, field["name"]])
        logger.error(value_type)
        definition = FIELDMAP.get(fqfieldname, FIELDMAP.get(value_type, None))
        if not definition or "pipeline" not in definition:
            continue
        source = definition["pipeline"]["source"].format(name=field["name"])
        target = definition["pipeline"]["target"].format(name=field["name"])
        pipelines["processors"] += expanded_processors(
            definition["pipeline"]["processors"], source, target
        )
    if pipelines["processors"]:
        logger.info(
            "update ingest pipeline {0} with {1}".format(pipeline_name, pipelines)
        )
        es.ingest.put_pipeline(pipeline_name, pipelines)
    else:
        es.ingest.delete_pipeline(pipeline_name)


def ingest(content, full_schema, index_name):
    # preprocess content and schema
    preprocess(content, full_schema)
    if full_schema:
        create_or_update_mapping(full_schema, index_name)
        if not STATES["pipelines_created"]:
            setup_ingest_pipelines(full_schema, index_name)
            STATES["pipelines_created"] = True
    info = {"expansion_fields": EXPANSION_FIELDS}
    logger.warn(str(info))
    postprocess(content, info)

    # now, ingest
    from pprint import pformat

    logger.warn(pformat(content))
    es = get_ingest_client()
    es_kwargs = dict(
        index=index_name,
        id=content["UID"],
        pipeline=_es_pipeline_name(index_name),
        body=content,
    )
    es.index(**es_kwargs)
