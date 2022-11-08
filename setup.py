# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


setup(
    name="collective.elastic.ingest",
    version="1.0",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/collective.elastic.ingest",
        "Source": "https://github.com/collective/collective.elastic.ingest",
        "Tracker": "https://github.com/collective/collective.elastic.ingest/issues",
    },
    packages=find_packages("src"),
    namespace_packages=["collective", "collective.elastic"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    # python_requires=">=3.6",
    install_requires=[
        "CacheControl",
        "celery",
        "elasticsearch>=7",
        "requests",
        "setuptools",
        "six",
    ],
)
