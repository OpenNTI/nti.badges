#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

def safestr(s):
    s = s.decode("utf-8") if isinstance(s, bytes) else s
    return unicode(s) if s is not None else None

class MetaBadgeObject(type):

    def __new__(cls, name, bases, dct):
        t = type.__new__(cls, name, bases, dct)
        if 'mimeType' not in dct:
            clazzname = getattr(cls, '__external_class_name__', name)
            clazzname = b'.' + clazzname.encode('ascii').lower()
            t.mime_type = t.mimeType = 'application/vnd.nextthought.badges' + clazzname        
        t.parameters = dict()
        return t
