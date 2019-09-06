# -*- coding: utf-8 -*-
from celery import Celery

import os

app = Celery(
    'collective.es.ingestion',
    broker=os.environ.get('CELERY_BROKER'),
)


@app.task(name='collective.es.ingestion.index')
def index(object_base_url):
    return 'indexed {0}'.format(object_base_url)


@app.task(name='collective.es.ingestion.unindex')
def unindex(object_base_url):
    return 'unindexed {0}'.format(object_base_url)
