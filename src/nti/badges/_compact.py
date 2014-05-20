#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import sys

PY3 = sys.version_info[0] >= 3
if PY3:  # pragma: no cover
    navstr = str
else:  # pragma: no cover
    navstr = bytes
