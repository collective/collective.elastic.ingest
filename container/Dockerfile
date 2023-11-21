# syntax=docker/dockerfile:1
FROM python:3.12-slim

ARG PACKAGE_VERSION

RUN <<EOT
    mkdir /configuration
    pip install --upgrade pip
    pip install "collective.elastic.ingest[opensearch,elasticsearch,redis,rabbitmq,sentry]==$PACKAGE_VERSION"
EOT

ENV MAPPINGS_FILE=/configuration/mappings.json \
    CELERY_CONCURRENCY=1 \
    CELERY_LOGLEVEL=info

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
