#!/usr/bin/env python
from __future__ import print_function
from setuptools import find_packages
import pkutils
import ongair

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requirements = list(pkutils.parse_requirements('requirements.txt'))
readme = pkutils.read('README.md')
author = ongair.__author__
license = ongair.__license__
version = ongair.__version__
project = ongair.__title__
description = ongair.__description__
email = ongair.__email__
user = 'ongair'

# TODO: Figuring out the right licence,
setup(
    name=project,
    version=version,
    url=pkutils.get_url(project, user),
    licence=license,
    author=author,
    install_requires=requirements,
    setup_requires=['pkutils>=0.12.4,<0.13.0'],
    scripts=['ongair-cli', 'ongair-monitor-cli'],
    author_email=email,
    description=description,
    packages=find_packages(),
    include_package_data=True,
    platforms=['MacOS X', 'Windows', 'Linux'],
    classifiers=[
        pkutils.LICENSES[license],
        pkutils.get_status(version),
        'Natural Language :: English',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Environment :: Console',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',

    ]

)
