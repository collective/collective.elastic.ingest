Changelog
=========


1.4.1 (unreleased)
------------------

- Fix OpenSearch / ElasticSearch switch. [ksuess]
- Update example mapping for nested field "NamedBlobFile": 
  "include_in_parent": true, allows to search with non-nested query.
  [ksuess]


1.4 (2023-08-17)
----------------

- Allow custom text analysis for blocks_plaintext. [ksuess]


1.3 (2023-08-17)
----------------

- Support OpenSearch. [ksuess]
- Fetch content expandend. Breaking: API expander expands on request to expand, else not.
  Check your preprocessings.json to not handle rid. It's handled in preprocessing.py per default.
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

- Add optional configuration of text analysis (stemmer, decompunder, etc)
  [ksuess]

- Keep source on rewrite 
  [ksuess]

- Initial release.
  [jensens]
