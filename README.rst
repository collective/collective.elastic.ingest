=========================
collective.elastic.ingest
=========================

Celery-Tasks for ElasticSearch or OpenSearch integration for Plone content

- auto-create ElasticSearch...
    - index
    - mapping from Plone schema using a flexible conversions file (JSON).
    - ingest-attachment pipelines using (same as above) file.
- task to
    - index a content object with all data given plus allowedRolesAndUsers and section (primary path)
    - unindex an content object
- configure from environment variables:
    - celery,
    - elasticsearch,
    - sentry logging (optional)


Installation
------------

Install ``collective.elastic.ingest`` (redis-ready) using pip::

    pip install collective.elastic.ingest redis

``collective.elastic.ingest`` requires ``elasticsearch``. Specifiy the version according your ``Elasticsearch`` app version.
For example::

    pip install 'elasticsearch~=7.0'


Starting
--------

Define the configuration as environment variables::

    CELERY_BROKER=redis://localhost:6379/0
    ELASTICSEARCH_INGEST_SERVER=localhost:9200
    ELASTICSEARCH_INGEST_USE_SSL=0
    PLONE_SERVICE=http://localhost:8080
    PLONE_PATH=Plone
    PLONE_USER=admin
    PLONE_PASSWORD=admin

or for OpenSearch::

    export OPENSEARCH_INGEST_SERVER=localhost:9200
    export OPENSEARCH_INGEST_USE_SSL=1

Optional (defaults used if not given)::

    ANALYSIS_FILE=/full/path/to/analysis.json
    MAPPINGS_FILE=/full/path/to/mappings.json
    PREPROCESSINGS_FILE=/full/path/to/preprocessings.json
    SENTRY_DSN= (disabled by default)

Then run celery::

    celery -A collective.elastic.ingest.celery.app worker -l info

Or with debug information::

    celery -A collective.elastic.ingest.celery.app worker -l debug


Text Analysis
-------------

Test analysis is optional. Skip this on a first installation.

Search results can be enhanced with a tailored text analysis.
This is an advanced topic.
You can find detailed information about text analysis in ElasticSearch documentation.
We provide an example analysis configuration for a better search for german compounded words.

Example: A document with the string 'Lehrstellenbörse' can be found by quering 'Lehrstelle' and also by quering 'Börse' with a ``decompounder`` with word list 'Lehrstelle, Börse' and an additional ``stemmer``.

The example analyzer configuration also applies a ``stemmer``, which can handle flexations of words, which is an important enhancement.
Even fuzzy search, which can be used without any analysis configuration, has its limits in a nice but complex language like german.

The analysis configuration is just a configuration of analyzers.
In the provided example are two of them: ``german_analyzer`` and ``german_exact``.
The first is the one to decompound words according the word list in `lexicon.txt`. A ``stemmer`` is added.
The second one is to allow also exact queries with a quoted search string. 
These two analyzers are to be applied to fields. You can apply them in your mapping.
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

The response delivers the tokens for the analyzed text "Lehrstellenbörse".

Note: The file ``elasticsearch-lexicon.txt`` with the word list used by the ``decompounder`` of the sample analysis configuration in ``analysis.json.example`` has to be located in the configuration directory of your elasticsearch server.


Source Code
-----------

The sources are in a GIT DVCS with its main branches at `github <https://github.com/collective/collective.elastic.ingest>`_.
There you can report issue too.

We'd be happy to see many forks and pull-requests to make this addon even better.

Maintainers are `Jens Klein <mailto:jk@kleinundpartner.at>`_, `Peter Holzer <mailto:peter.holzer@agitator.com>`_ and the BlueDynamics Alliance developer team.
We appreciate any contribution and if a release is needed to be done on pypi, please just contact one of us.
We also offer commercial support if any training, coaching, integration or adaptions are needed.


Contributions
-------------

Initial implementation was made possible by `Evangelisch-reformierte Landeskirche des Kantons Zürich <https://zhref.ch/>`_.

Idea and testing by Peter Holzer

Concept & code by Jens W. Klein

Text analysis code and configuration Katja Süss



Install for development
-----------------------

- clone source code repository,
- enter repository directory
- recommended: create a virtualenv ``python -mvenv env``
- development install ``./bin/env/pip install -e .``
- add redis support ``./bin/env/pip install redis``.
- load environment configuration ``source .env``.


Todo
----

- query status of a task
- simple statistics about tasks-count: pending, done, errored
- celery retry on failure, i.e. restart of ElasticSearch, Plone, ...

License
-------

The project is licensed under the GPLv2.
