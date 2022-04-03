.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

=========================
collective.elastic.ingest
=========================

Celery-Tasks for ElasticSearch Integration for Plone content

- auto-create ElasticSearch...
    - index
    - mapping from Plone schema using a flexible conversions file (JSON).
    - ingest-attachment pipelines using (same as above) file.
- task to
    - index an content object with all data given
    - unindex an content object
- configure from environment variables:
    - celery,
    - elasticsearch,
    - sentry logging (optional)


Installation
------------

Install ``collective.elastic.ingest`` (redis-ready) using pip::

    pip install collective.elastic.ingest redis


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

Optional (defaults used if not given)::

    ANALYSIS_FILE=/full/path/to/analysis.json
    MAPPINGS_FILE=/full/path/to/mappings.json
    PREPROCESSINGS_FILE=/full/path/to/preprocessings.json
    SENTRY_DSN= (disabled by default)

Then run celery::

    celery worker -A collective.elastic.ingest.celery.app -l info

Source Code
-----------

The sources are in a GIT DVCS with its main branches at `github <http://github.com/collective/collective.elastic.ingest>`_.
There you can report issue too.

We'd be happy to see many forks and pull-requests to make this addon even better.

Maintainers are `Jens Klein <mailto:jk@kleinundpartner.at>`_, `Peter Holzer <mailto:peter.holzer@agitator.com>`_ and the BlueDynamics Alliance developer team.
We appreciate any contribution and if a release is needed to be done on pypi, please just contact one of us.
We also offer commercial support if any training, coaching, integration or adaptions are needed.


Contributions
-------------

Initial implementation was made possible by `Evangelisch-reformierte Landeskirche des Kantons Zürich <http://zhref.ch/>`_.

Idea and testing by Peter Holzer

Concept & code by Jens W. Klein

Contributors:

- no others so far

Install for development:

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
