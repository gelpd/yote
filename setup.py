#!/usr/bin/env python

import os
from codecs import open
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
packages = ['yote']
requires = [
    "orjson>=3,<4"
]
test_requirements = [
]

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name="Yote",
    version="0.1",
    description="Organize and write machine learning logs and metrics easily.",
    long_description=readme,
    long_description_content_type='text/markdown',
    author="gelpd",
    author_email="gelpd@protonmail.com",
    url="https://github.com/gelpd/yote",
    packages=packages,
    package_data={'': ['LICENSE', 'NOTICE']},
    package_dir={'yote': 'yote'},
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=requires,
    license="MIT",
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    tests_require=test_requirements,
    extras_require={
    },
    project_urls={
        'Source': 'https://github.com/gelpd/yote',
    },
)