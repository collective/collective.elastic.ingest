# -*- coding: utf-8 -*-
from collective.elastic.ingest.elastic import get_ingest_client
from collective.elastic.ingest.mapping import create_or_update_mapping
from collective.elastic.ingest.mapping import FIELDMAP
from collective.elastic.ingest.mapping import iterate_schema
from collective.elastic.ingest.preprocessing import preprocess
from elasticsearch.exceptions import NotFoundError


import six
import logging

logger = logging.getLogger(__name__)

STATES = {"pipelines_created": False}

PIPELINE_PREFIX = "attachment_ingest"


def _es_pipeline_name(index_name):
    return "{0}_{1}".format(PIPELINE_PREFIX, index_name)


def setup_ingest_pipelines(full_schema, index_name):
    es = get_ingest_client()
    pipeline_name = _es_pipeline_name(index_name)
    do_create = False
    try:
        es.ingest.get_pipeline(pipeline_name)
    except NotFoundError:
        do_create = True
    if not do_create:
        return
    pipelines = {
        "description": "Extract Plone Binary attachment information",
        "processors": [],
    }
    for section_name, schema_name, field in iterate_schema(full_schema):
        value_type = field.get("value_type", field["field"])
        fqfieldname = "/".join([section_name, schema_name, field["name"]])
        definition = FIELDMAP.get(fqfieldname, FIELDMAP.get(value_type, None))
        if not definition or "processor" not in definition:
            continue
        attachment = {}
        pipelines["processors"].append({"attachment": attachment})
        for key, value in definition["processor"]["attachment"].items():
            if isinstance(value, six.string_types):
                attachment[key] = value.format(name=field["name"])
            else:
                attachment[key] = value
    logger.warning(str(pipelines))
    if pipelines["processors"]:
        es.ingest.put_pipeline(pipeline_name, pipelines)
    else:
        es.ingest.delete_pipeline(pipeline_name)


def ingest(content, full_schema, index_name):
    # preprocess content and schema
    preprocess(content, full_schema, index_name)
    if full_schema:
        if not STATES["pipelines_created"]:
            setup_ingest_pipelines(full_schema, index_name)
            STATES["pipelines_created"] = True
        create_or_update_mapping(full_schema, index_name)
