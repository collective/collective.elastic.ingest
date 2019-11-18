# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="collective.elastic.ingest",
    version="1.0a1",
    description="Queue runner for collective.elastic.plone",
    long_description=long_description,
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
        "elasticsearch",
        "requests",
        "setuptools",
        "six",
    ],
)
