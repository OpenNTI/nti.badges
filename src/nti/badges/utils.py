#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)


class MetaBadgeObject(type):

    def __new__(cls, name, bases, dct):
        t = type.__new__(cls, name, bases, dct)
        if 'mimeType' not in dct:
            clazzname = getattr(cls, '__external_class_name__', name)
            clazzname = b'.' + clazzname.encode('ascii').lower()
            t.mimeType = 'application/vnd.nextthought.badges' + clazzname
            t.mime_type = t.mimeType
        t.parameters = dict()
        return t
