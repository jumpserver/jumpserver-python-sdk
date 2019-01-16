#!/bin/bash
# coding: utf-8
# Copyright (c) 2018
# Gmail: liuzheng712
#
set -ex
[ -d dist ] && rm -f dist/* 
python setup.py sdist # && \

if [ "$1" == "upload" ];then
    twine upload dist/*.tar.gz
fi
