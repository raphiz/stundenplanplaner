#!/usr/bin/env python
# encoding: utf-8

import os
from setuptools import setup, find_packages


setup(
    name="planner",
    version="0.1.0.dev0",
    packages=['planner'],
    author="Raphael Zimmermann",
    author_email="dev@raphael.li",
    url="https://github.com/raphiz/hsr_timetable",
    description="Like flask - but for static sites",
    long_description=("For more information, please checkout the `Github Page "
                      "<https://github.com/raphiz/hsr_timetable>`_."),
    license="MIT",
    platforms=["Linux", "BSD", "MacOS"],
    include_package_data=True,
    zip_safe=False,
    install_requires=open('./requirements.txt').read(),
    test_suite='tests',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        "Programming Language :: Python :: Implementation :: CPython",
        'Development Status :: 4 - Beta',
    ],
)
