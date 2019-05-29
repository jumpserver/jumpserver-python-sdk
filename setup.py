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

with open('requirements.txt', 'r') as f:
    requirements = [x.strip() for x in f.readlines()]

setup(
    name='jumpserver-python-sdk',
    version=version,
    description='Jumpserver python sdk tools',
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords='jms jumpserver',
    packages=['jms'],
    author='Jumpserver team',
    author_email='support@fit2cloud.com',
    install_requires=requirements,
    include_package_data=True,
    data_files=[('requirements', ['requirements.txt'])],
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
