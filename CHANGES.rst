Changelog
=========

2.0.0rc9 (2023-12-04)
---------------------

- Enhancement: OCI image documentation. [jensens]
- Enhancement: Strip trailing slash from ``PLONE_SERVICE`` URL. [jensens]
- Enhancement: Add ``PLONE_SITE_PREFIX_METHOD`` env var:
  ``keep`` lets the prefix untouched, ``strip`` removes it. [jensens]
- Breaking: Rename ``PLONE_PATH`` to ``PLONE_SITE_PREFIX_METHOD``. [jensens]


2.0.0rc8 (2023-12-01)
---------------------

- Fix bug in field cache on full_remove [jensens]
- Fix bug in full schema cache on full_remove [jensens]
- Fix new bug in vocab transforming action [jensens]


2.0.0rc7 (2023-12-01)
---------------------

- Fix the wrong OPENSEARCH fix [jensens]


2.0.0rc5 (2023-12-01)
---------------------

- Fix: Plone schema caching logic was broken. [jensens]
- Fix: Remove unnecessary ``batching`` on preprocessing. [jensens]
- Fix: Add missing ``zope.schema._field.Set`` to examples mapping. [jensens]
- Enhancement: Move vocabulary and section handling to preprocessing.
  Turn ``ingest`` package into module. [jensens]
- Fix: Get OPENSEARCH from c.e.ingest module and do n`ot dup here. [jensens]
- Fix: Remove leftover/defunct blocks_plaintext handling.
  This was moved already to preprocessing. [jensens]


2.0.0rc4 (2023-11-30)
---------------------

- Fix: Analysis creation overruled index settings. [jensens]
- Fix Do not fail in preprocessing fullremove, when source does not exist. [jensens]
- Fix: Optimize preprocessing.json to do fullremove for volto blocks and add schema for blocks_plaintext. [jensens]
- Fix: In preprocessing rewrite, do remove source field. [jensens]
- Fix: @cesp schema (aka full_schema) was not cached. Now cache for 60s [jensens]
- Fix: Do not fail in preprocessing full_remove, when full_schema is None. [jensens]
- Enhancement: Default preprocessings removes lock and parent fields . [jensens]

2.0.0rc3 (2023-11-28)
---------------------

- Feature: set env ``INDEX_SSL_SHOW_WARN=1`` to pass as ``ssl_show_warn`` kwarg in OpenSearch client [jensens]
- Feature: set env ``INDEX_SSL_ASSERT_HOSTNAME=1`` to pass as ``ssl_assert_hostname`` kwarg in OpenSearch client [jensens]


2.0.0rc2 (2023-11-28)
--------------------

- Fix: Default address for ElasticSearch needs ``https://`` prefix [jensens]
- Feature: set env ``INDEX_VERIFY_CERTS=1`` to pass as ``verify_certs`` kwarg in OpenSearch client [jensens]

2.0.0rc1 (2023-11-27)
---------------------

- Add a note to the README about the steps needed if upgrading from 1.x [jensens]
- Add a note to the README about exposed port 9200 and a hint to block it if needed. [jensens]

2.0.0b11 (2023-11-22)
---------------------

- Packaging: remove namespace level empty ``__init__.py`` to make interoperable with multiple ``collective.*`` namespaces while in editable mode [jensens]

2.0.0b10 (2023-11-21)
---------------------

- add an extra "sentry" and install by default in Dockerfile [jensens]

2.0.0b9 (2023-11-20)
--------------------

- Fix CI to not release when tests are failing [jensens]
- Fix tests [jensens]
- Remove check for elasticsearch/opensearch-py library version, we already pin this down in pyproject.toml [jensens]


2.0.0b8 (2023-11-20)
--------------------

- Add documentation for preprocessings [jensens]
- Remove 2 of the 4 static preprocessings and use preprocessings file for those. [jensens]
- Refactor and add  preprocessings to be more consistent and less verbose.
  Attention: JSON file format changed [jensens]


2.0.0b7 (2023-11-16)
--------------------

- Fix ElasticSearch support. [jensens]
- Add examples for a docker-compose setup for both, OpenSearch and ElasticSearch. [jensens]


2.0.0b6 (2023-11-16)
--------------------

- Fix OpenSearch / ElasticSearch switch. [ksuess]
- Update example mapping for nested field "NamedBlobFile":
  "include_in_parent": true, allows to search with non-nested query.
  [ksuess]
- code-style: black & isort [jensens]
- Add support for Plone ClassicUI based sites (no Volto blocks available) [jensens]
- Move mappings.json, analysis.json.example with its lexicon out of code into examples directory and pimped docs on how to use all this.
  [jensens]
- Add docker-compose file to start OpensSearch to example directory and move `.env` to example too.
  [jensens]
- rename `ELASTIC_*` environment variables to have an consistent naming scheme, see README for details. [jensens]
- Add tox, Github Actions, CI and CD. [jensens]
- Refactor field-map loading to not happen on startup. [jensens]
- Remove Support for OpenSearch 1.x and ElasticSearch < 8 [jensens]
- Rename .elastic.get_ingest_client to .client.get_client [jensens]
- Do not initialize a new client for each operation, but use a thread local cached one.
  This speeds up indexing a lot. [jensens]
- Fix Sentry integration to not trigger if env var is empty string. [jensens]


1.4 (2023-08-17)
----------------

- Allow custom text analysis for blocks_plaintext. [ksuess]


1.3 (2023-08-17)
----------------

- Support OpenSearch. [ksuess]
- Fetch content expanded. Breaking: API expander expands on request to expand, else not.
  Check your `preprocessings.json` to not handle rid. It's handled in preprocessing.py per default.
  [ksuess]


1.2 (2023-07-03)
----------------

- Update example of preprocessing.json [ksuess]
- Update README.rst: instruction on how to start celery [ksuess]
- Add fallback section [ksuess]


1.1 (2023-03-03)
----------------

- Index allowedRolesAndUsers and section (primary path) [ksuess]


1.0 (2022-11-08)
----------------

- Update to elasticsearch-py 8.x
  [ksuess]

- Add optional configuration of text analysis (stemmer, decompounder, etc)
  [ksuess]

- Keep source on rewrite
  [ksuess]

- Initial release.
  [jensens]
