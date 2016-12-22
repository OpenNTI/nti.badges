#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import sys
import types

PY3 = sys.version_info[0] == 3

if PY3:  # pragma: no cover
    text_type = str
    class_types = type,
    string_types = str,
    integer_types = int,
    binary_type = bytes
else:
    binary_type = str
    text_type = unicode
    string_types = basestring,
    integer_types = (int, long)
    class_types = (type, types.ClassType)

if PY3: # pragma: no cover
    _unicode = unicode
else:
    _unicode = lambda s: s

def to_unicode(s, encoding='utf-8', err='strict'):
    """
    Decode a byte sequence and unicode result
    """
    s = s.decode(encoding, err) if isinstance(s, bytes) else s
    return _unicode(s) if s is not None else None
