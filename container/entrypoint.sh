#!/bin/bash
set -o errexit

CONCURRENCY="${CELERY_CONCURRENCY:=1}"
LOGLEVEL="${CELERY_LOGLEVEL:=info}"

celery -A collective.elastic.ingest.celery.app worker -c $CONCURRENCY -l $LOGLEVEL
