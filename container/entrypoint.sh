#!/bin/bash
set -o errexit

celery -A collective.elastic.ingest.celery.app worker -c $CELERY_CONCURRENCY -l $CELERY_LOGLEVEL
