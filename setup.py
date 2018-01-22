#!/usr/bin/env python

import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('jms/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')


with open('README.md', 'rb') as f:
    readme = f.read().decode('utf-8')

setup(
    name='jumpserver-python-sdk',
    version=version,
    description='Jumpserver python sdk tools',
    long_description=readme,
    keywords='jms jumpserver',
    packages=['jms'],
    author='Jumpserver team',
    author_email='ibuler@qq.com',
    install_requires=[
        'paramiko==2.4.0s',
        'requests>=2.11.1',
        'cachetools>=2.0.0',
        'pytz==2017.2',
        'pyte==0.5.2',
    ],
    include_package_data=True,
    url='http://jumpserver.org',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)
