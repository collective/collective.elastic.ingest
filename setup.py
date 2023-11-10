# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CHANGES.rst").read(),
        open("CONTRIBUTORS.rst").read(),
    ]
)


setup(
    name="collective.elastic.ingest",
    version="1.4.1.dev0",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/collective.elastic.ingest",
        "Source": "https://github.com/collective/collective.elastic.ingest",
        "Tracker": "https://github.com/collective/collective.elastic.ingest/issues",
    },
    description="Addon for ElasticSearch integration with Plone",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone",
    packages=find_packages("src"),
    namespace_packages=["collective", "collective.elastic"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "CacheControl",
        "celery",
        "requests",
        "setuptools",
    ],
    extras_require={
        "redis": ["celery[redis]"],
        "rabbitmq": ["celery[librabbitmq]"],
        "opensearch": ["opensearch-py"],
        "elasticsearch7": ["elasticsearch~=7.0"],
        "elasticsearch8": ["elasticsearch~=8.0"],
    },
)
