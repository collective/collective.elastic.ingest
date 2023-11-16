# syntax=docker/dockerfile:1
FROM python:3.12-slim

ARG IMAGE_VERSION
ARG PACKAGE_VERSION

# TODO: use https://github.com/opencontainers/image-spec/blob/main/annotations.md
LABEL version="${PACKAGE_VERSION}-${IMAGE_VERSION}"
LABEL description="Ingestion service queue runner between Plone RestAPI and ElasticSearch or OpenSearch."
LABEL maintainer="Jens Klein"
LABEL org.label-schema.name="collective.elastic.ingest"
LABEL org.label-schema.description="Ingestion service queue runner between Plone RestAPI and ElasticSearch or OpenSearch."
LABEL org.label-schema.vendor="Klein & Partner KG and Contributors"

RUN <<EOT
    pip install --upgrade pip
    pip install "collective.elastic.ingest[opensearch,elasticsearch,redis,rabbitmq]==$PACKAGE_VERSION"
EOT

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
