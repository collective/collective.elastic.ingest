Changelog
=========

2.0.0rc1 (2023-11-27)
--------------------

- Add a note to the README about the steps needed if upgrading from 1.x [jensens]
- Add a note to the README about exposed port 9200 and a hint to block it if needed. [jensens]

2.0.0b11 (2023-11-22)
--------------------

- Packaging: remove namespace level empty ``__init__.py`` to make interoperable with multiple ``collective.*`` namespaces while in editable mode [jensens]

2.0.0b10 (2023-11-21)
--------------------

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
