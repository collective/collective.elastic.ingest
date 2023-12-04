=========================
collective.elastic.ingest
=========================

Ingestion service queue runner between Plone RestAPI and ElasticSearch 8+ or OpenSearch 2+.
Provides Celery-tasks to asynchronous index Plone content.

- auto-create Open-/ElasticSearch...
    - index
    - mapping from Plone schema using a flexible conversions file (JSON),
    - ingest-attachment pipelines using (same as above) file.
- task to
    - index a content object with all data given plus allowedRolesAndUsers and section (primary path)
    - unindex an content object
- configure from environment variables:
    - celery,
    - elasticsearch or opensearch
    - sentry logging (optional)

.. contents:: Table of Contents


Installation
============

We recommended to use a Python virtual environment, create one with ``python3 -m venv venv``, and activate it in the current terminal session with ``source venv/bin/activate``.

Install ``collective.elastic.ingest`` ready to use with redis and opensearch::

    pip install collective.elastic.ingest[redis,opensearch]

Depending on the queue server and index server used, the extra requirements vary:

- queue server: ``redis`` or ``rabbitmq``.
- index server: ``opensearch`` or ``elasticsearch``.


Configuration
=============

Configuration is done via environment variables and JSON files.

-----------
Environment
-----------

Environment variables are:

INDEX_OPENSEARCH
    Whether to use OpenSearch or ElasticSearch.

    Default: 1

INDEX_SERVER
    The URL of the ElasticSearch or OpenSearch server.

    Default: localhost:9200

INDEX_USE_SSL
    Whether to use a secure TLS connection or not.

    Default: 0

INDEX_VERIFY_CERTS
    Whether to verify TLS certificates on secure connection or not.

    Default: 0

INDEX_SSL_SHOW_WARN
    Whether to warn for unverified TLS request is made or not.

    Default: 0

INDEX_SSL_ASSERT_HOSTNAME
    Whether to assert the hostname in TLS request or not.

    Default: 0

INDEX_LOGIN
    Username for the ElasticSearch 8+ or OpenSearch server.

    Default: admin

INDEX_PASSWORD
    Password for the ElasticSearch 8+ or OpenSearch server.

    Default: admin


CELERY_BROKER
    The broker URL for Celery.
    See `docs.celeryq.dev <https://docs.celeryq.dev/>`_ for details.

    Default: ``redis://localhost:6379/0``

PLONE_SERVICE
    Base URL of the Plone Server

    Default: ``http://localhost:8080``

PLONE_SITE_PREFIX_PATH
    Path to the site to index at the Plone Server.

    Default: ``Plone``

PLONE_SITE_PREFIX_METHOD
    Wether to keep the prefix path while requesting the content from the Plone Server or not.
    Allowed values: ``strip``, ``keep``

    On ``keep``, the prefix path is kept in the index/schema path.
    If the ``PLONE_SERVICE`` runs under ``http://localhost:8080`` and the ``PLONE_SITE_PREFIX_PATH`` is ``Plone``,
    the index/schema base path where the ingest service fetches its data and schema from is ``http://localhost:8080/Plone``.

    On ``strip``, the prefix path is stripped from the index/schema path.
    If the ``PLONE_SERVICE`` runs under ``https://www.mydomain.tld`` and the ``PLONE_SITE_PREFIX_PATH`` is ``Plone``,
    the index/schema base path is ``https://www.mydomain.tld``.

    Default: ``keep``

PLONE_USER
    Username for the Plone Server, needs to have at least Site Administrator role.

    Default: admin

PLONE_PASSWORD
    Password for the Plone Server.

    Default: admin

MAPPINGS_FILE
    Absolute path to the mappings configuration file.
    Configures field mappings from Plone schema to ElasticSearch.

    No default, must be given.

PREPROCESSINGS_FILE
    Configures preprocessing of field values before indexing.

    Default: Uses a defaults file of this package.

ANALYSIS_FILE
    (optional) Absolute path to the analysis configuration file.

SENTRY_DSN
    (optional) Sentry DSN for error reporting.

    Default: disabled

SENTRY_INGEST
    (optional) Enable sentry reporting in Celery.
    Reason behind this is, SENTRY_DSN_DSN is possibly provided in a Plone environment when this package is used as a library.
    To not override any existing sentry-sdk initialization, this flag is used to enable sentry reporting specifically in ingest mode.
    Allowed values: true, false

    Default: false

Upgrade
-------

Coming from version 1.x of this package, in 2.x you need to change some names of the environment variables.

- ``ELASTICSEARCH_INGEST_*`` to ``INDEX_*``
- ``OPENSEARCH*`` to ``INDEX_OPENSEARCH``
- ``PLONE_PATH`` to ``PLONE_SITE_PREFIX_PATH``.
  Additional a new option ``PLONE_SITE_PREFIX_METHOD=strip`` to strip the path prefix from the index/schema path is available.
  See above for details.
- If you use Sentry, additional ``SENTRY_INGEST=true`` is needed.

----------
JSON-Files
----------


``mappings.json``
-----------------

The mappings file is a JSON file with the following structure:

First level: ``Key: Value`` Pairs

The key is
- either a fully qualified field name (path) to the field in the schema (``behaviors/...`` or ``types/...``), like ``behaviors/plone.basic/title``.
- or the dotted name of a zope.schema based field type, like ``plone.namedfile.field.NamedBlobImage``.

The value is an instruction how to map this specific field or field type to OpenSearch or ElasticSearch.
The actual mapping send to the index server is generated from this instruction and the full schema fetched from Plone.
At generation time, the process iterates over the full schema and applies the mapping instructions to each field.

At first the instruction lookup is done by the fully qualified field name.
If no instruction is found, the dotted name of the field type is used.

There are two types of instructions: Simple ones and complex ones.

The **simple instruction** has the ``type`` defined as a top level key.
The type is the mapping type defined by the index server for the mapping, like ``text`` or ``boolean``.
For some types this is enough, others take additional keys.
The ``nested`` type is such a type.
Here the keys ``properties`` and ``dynamic`` are required.
Those keys are provided on top level.

The **complex instruction** has the ``type`` defined in the ``definition`` key.
The ``definition`` key is a mapping with the ``type`` key and the same additional keys for the definition of the field type as for the simple one.
There are two other possible top-level keys for complex instructions: ``detections`` and ``pipelines``.

A ``detection`` is a method to do something based on the schemas field parameters.
At the moment this is only used to detect a ``value_type`` of a Plone list field or similar.
This detector is registered as ``replace``.

A ``pipeline`` is a method to add a processing pipeline to the field.
Those are used to ingest binary data like images or PDFs, but any other pipeline can be configured.
The pipeline is registered and executed.
The configuration of a pipeline consists of a ``source``, a ``target``, ``type`` as above for defining the target data, ``processors``, and an ``expansion``.

- source is the field name with the input data for the pipeline.
- target is the field name for the output data of the pipeline.
- type is the definition of the target field.
- processors are a list of processors to apply to the data.
- expansion not directly mapping related, but configured here as it defines where in a postprocessing step the data is fetched from.
  Binary data is not provided in the content data, only a link where to download.


``preprocessings.json``
-----------------------

Pre-processings are steps done before anything else is processed.
They run on the raw data from the Plone REST API, the full schema fetched from the Plone backend, and the full content object fetched from the Plone backend.
Each preprocessing is a function that takes the data and modifies the full schema or full content.

The pre-processings-file consists of list a processing instructions records.

Each record is a mapping  with a ``match``, an ``action`` and a ``configuration``.

The match call an function that returns a boolean value.
If the value is true, the action is executed, otherwise skipped.

There are two matches available

``always``
    Always matches.

    Example configuration ``{"match": {"type": "always"}, ...}``

    This is the default if no match is given.

``content_exists``
    Matches if the field ``configuration["path"]`` is present in the content data.
    Path can point to a field ``foo`` or check for its sub entries like ``foo/bar/baz``.

    Example configuration ``{"match": {"type": "content_exists", "path": "foo"}, ...}``

The action is a function that takes the full schema and content data, the configuration, and then modifies the full schema or full content.

These actions ar available:

``additional_schema``
    Adds an additional schema to the full schema.
    The configuration must a valid schema to add.

``rewrite``
    Moves content data from one position in the field-tree to another.
    The configuration must be a mapping with ``source`` and ``target`` keys.
    The value of ``source`` is the path to the data to move.
    The value of ``target`` is the path to the new location of the data (missing containers are created).
    The value of ``enforce`` is a boolean value (default: False). If True, the source must exist, otherwise an error is raised.

    Example: ``"configuration": {"source": "@components/collectiveelastic/blocks_plaintext",  "target": "blocks_plaintext", "enforce": false}``

``remove``
    Deletes a field or sub-field from the content data.
    The value of ``target`` is the path to the data to delete.

``field_remove``
    Deletes a field from the full schema and its field value from the content.
    The value of ``section`` is the section (one of ``behaviors`` or ``types``)
    The value of ``name`` is the name of the behavior or type.
    The value of ``field`` is the name of the field to delete.

``full_remove``
    Deletes a full behavior or type with all its fields from the full schema and its fields values from the content.
    The value of ``section`` is the section (one of ``behaviors`` or ``types``)
    The value of ``name`` is the name of the behavior or type.

``remove_empty``
    Deletes all empty fields from the content data.
    A field is considered empty if it is ``None``, ``[]``, ``{}`` or ``""``


``analysis.json``
-----------------

This file provides the index with analyzers to be used in the ``mappings.json`` files different definition sections (top-level, nested, complex or pipeline target).

Read more on this topic in the dedicated section below.


Start up
========

Run celery worker::

    celery -A collective.elastic.ingest.celery.app worker -c 1 -l info

Or with debug information::

    celery -A collective.elastic.ingest.celery.app worker -c 1 -l debug

The number is the concurrency of the worker.
For production use, it should be set to the number of Plone backends available for indexing load.


OCI Image usage
===============

For use in Docker, Podman, Kubernetes, ..., an OCI image is provided at the `Github Container Registry <https://github.com/collective/collective.elastic.ingest/pkgs/container/collective.elastic.ingest>`_.

The environment variables above are used as configuration.

Additional the following environment variables are used:

CELERY_CONCURRENCY
    The number of concurrent tasks to run.

    Default: 1

CELERY_LOGLEVEL
    The log level for celery.

    Default: info

The ``MAPPINGS_FILE`` variable defaults to ``/configuration/mappings.json``.
By default no file is present.

When a mount is provided to ``/configuration``, the mappings file can be placed there.
Alternatively, the mappings file can be provided as a `configs element in docker compose <https://docs.docker.com/compose/compose-file/08-configs/>`_ or as a `configmap <https://kubernetes.io/docs/concepts/configuration/configmap/>`_ in Kubernetes.


Examples
========

Example configuration files are provided in the `./examples <https://github.com/collective/collective.elastic.ingest/tree/main/examples>`_ directory.

------------------------------
OpenSearch with Docker Compose
------------------------------

Location: ``examples/docker-os/*``

A docker-compose file ``docker-compose.yml`` and a ``Dockerfile`` to start an Ingest, Redis and an OpenSearch server with dashboard is provided.

Precondition:

- Docker and docker-compose are installed.
- Max virtual memory map needs increase to run this: ``sudo sysctl -w vm.max_map_count=262144`` (not permanent, `see StackOverflow post <https://stackoverflow.com/questions/66444027/max-virtual-memory-areas-vm-max-map-count-65530-is-too-low-increase-to-at-lea>`_).
- enter the directory ``cd examples/docker``

Steps to start the example OpenSearch Server with the ``ingest-attachment`` plugin installed:

- locally build the custom OpenSearch Docker image enriched with the plugin using::

    docker buildx use default
    docker buildx build --tag opensearch-ingest-attachment:latest Dockerfile

- start the cluster with ``docker-compose up``.

Now you have an OpenSearch server running on ``http://localhost:9200`` and an OpenSearch Dashboard running on ``http://localhost:5601`` (user/pass: admin/admin).
The OpenSearch server has the ``ingest-attachment`` plugin installed.
The plugin enables OpenSearch to extract text from binary files like PDFs.

A Redis server is running on ``localhost:6379``.

Additional the ingest worker runs and is ready to index content from a Plone backend.

Open another terminal.

In another terminal window `run a Plone backend <https://6.docs.plone.org/install/index.html>`_ at ``http://localhost:8080/Plone`` with the add-on `collective.elastic.plone` installed.
There, create an item or modify an existing one.
You should see the indexing task in the celery worker terminal window.

For production use, please **check that the port 9200 is not exposed to the internet**.
For a good measure block it with a firewall rule.

---------------------------------
ElasticSearch with Docker Compose
---------------------------------

Location: ``examples/docker-es/*``

A docker-compose file ``docker-compose.yml`` to start an Ingest, Redis and an ElasticSearch server with Dejavu dashboard is provided.

Precondition:

- Docker and docker-compose are installed.
- Max virtual memory map needs increase to run this: ``sudo sysctl -w vSITE_PREFIXm.max_map_count=262144`` (not permanent, `see StackOverflow post <https://stackoverflow.com/questions/66444027/max-virtual-memory-areas-vm-max-map-count-65530-is-too-low-increase-to-at-lea>`_).
- enter the directory ``cd examples/docker-es``

Run the cluster with::

    source .env
    docker-compose up

First you need to set the passwords for the ElasticSearch, execute the following command and note the passwords printed on the console::

    docker exec -it elasticsearch /usr/share/elasticsearch/bin/elasticsearch-setup-passwords auto

Find the password for the user ``elastic`` and set it in the environment variable ``INDEX_PASSWORD`` in the ``.env`` file.
Stop the cluster (Ctrl-C), ``source .env`` with the new settings and start it again (as above).

Now you have an ElasticSearch server running on ``http://localhost:9200`` and an Dejavu Dashboard running on ``http://localhost:1358``.
(The ElasticSearch server has the ``ingest-attachment`` plugin installed by default).

A Redis server is running on ``localhost:6379``.

Additional the ingest worker runs and is ready to index content from a Plone backend.

Open another terminal.

In another terminal window `run a Plone backend <https://6.docs.plone.org/install/index.html>`_ at ``http://localhost:8080/Plone`` with the add-on `collective.elastic.plone <https://github.com/collective/collective.elastic.plone>`_ installed.
There, create an item or modify an existing one.
You should see the indexing task in the celery worker terminal window.

For production use, please **check that the port 9200 is not exposed to the internet**.
For a good measure block it with a firewall rule.

------------------
Local/ Development
------------------

Location: ``examples/docker/local/*``

A very basic mappings file ``examples/docker/local/mappings.json`` is provided.
To use it set ``MAPPINGS_FILE=examples/mappings-basic.json`` and then start the celery worker.
An environment file ``examples/docker/local/.env`` is provided with the environment variables ready to use for local startup.

Run ``source examples/.env`` to load the environment variables.
Then start the celery worker with ``celery -A collective.elastic.ingest.celery.app worker -l debug``.

-----------------------------------------
Complex Mapping With German Text Analysis
-----------------------------------------

Location: ``examples/docker/analysis/*``

A complex mappings file with german text analysis configured, ``mappings-german-analysis.json`` is provided.
It comes together with the matching analysis configuration file ``analysis-german.json`` and a stub lexicon file ``elasticsearch-lexicon-german.txt``.
Read the next section for more information about text analysis.


Text Analysis
=============

Test analysis is optional.
Skip this on a first installation.

Search results can be enhanced with a tailored text analysis.
The simple fuzzy search, which can be used without any analysis configuration, has its limits.
This is even more true in complex languages like German.

This is an advanced topic.

You can find detailed information about `text analysis in the ElasticSearch documentation <https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis.html>`_.
We provide an example analysis configuration for a better search for German compounded words.

Example: A document with the string 'Lehrstellenbörse' can be found by querying 'Lehrstelle'.
It shall be found too by querying 'Börse' using a *decompounder* with a word list 'Lehrstelle, Börse' and an additional *stemmer*.
The example analyzer configuration applies a *stemmer*, which can handle inflections of words.
This is an important enhancement for better search results.

The analysis configuration is a configuration of analyzers.
The example provided here uses two of them: ``german_analyzer`` and ``german_exact``.

The first decompounds words according the word list in ``lexicon.txt``.
A *stemmer* is added.

The second one is to allow also exact queries with a quoted search string.

These two analyzers are to be applied to fields.
You can apply them in your mapping.

Example::

    "behaviors/plone.basic/title": {
        "type": "text",
        "analyzer": "german_analyzer",
        "fields": {
            "exact": {
                "type": "text",
                "analyzer": "german_exact_analyzer"
            }
        }
    },

Check your configured analysis with::

    POST {{elasticsearchserver}}/_analyze

    {
        "text": "Lehrstellenbörse",
        "tokenizer": "standard",
        "filter": [
            "lowercase",
            "custom_dictionary_decompounder",
            "light_german_stemmer",
            "unique"
        ]
    }

The response delivers the tokens for the analyzed text 'Lehrstellenbörse'.

Note: The file ``elasticsearch-lexicon.txt`` with the word list used by the ``decompounder`` of the sample analysis configuration in ``analysis.json.example`` has to be located in the configuration directory of your elasticsearch server.


Source Code
===========

The sources are in a GIT DVCS with its main branches at `github <https://github.com/collective/collective.elastic.ingest>`_.
There you can report issues too.

We'd be happy to see many forks and pull-requests to make this addon even better.

Maintainers are `Jens Klein <mailto:jk@kleinundpartner.at>`_, `Katja Suess <https://github.com/rohberg>`_ and the BlueDynamics Alliance developer team.
We appreciate any contribution and if a release is needed to be done on PyPI, please just contact one of us.
We also offer commercial support if any training, coaching, integration or adaptions are needed.


Installation for development
============================

- clone source code repository,
- enter repository directory
- recommended: create a Virtualenv ``python -mvenv env``
- development install ``./bin/env/pip install -e .[test,redis,opensearch]``
- load environment configuration ``source examples/.env``.


License
=======

The project is licensed under the GPLv2.
