#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import os
import sys
import logging

__version__ = '0.0.3'

formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                              datefmt='%a, %d %b %Y %H:%M:%S')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(BASE_DIR)
PROJECT_DIR = os.path.dirname(APP_DIR)
sys.path.extend([BASE_DIR, APP_DIR, PROJECT_DIR])

from .config import URL_MAP
from .auth import Auth
from .api import Request, AppService, UserService
