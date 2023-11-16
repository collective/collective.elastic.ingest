# syntax=docker/dockerfile:1
FROM python:3.12-slim

ARG IMAGE_VERSION
ARG PACKAGE_VERSION

RUN <<EOT
    pip install --upgrade pip
    pip install "collective.elastic.ingest[opensearch,elasticsearch,redis,rabbitmq]==$PACKAGE_VERSION"
EOT

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
