#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope import component

from nti.externalization import interfaces as ext_interfaces
from nti.externalization.datastructures import InterfaceObjectIO

from . import interfaces

@component.adapter(interfaces.IBadgeClass)
@interface.implementer(ext_interfaces.IInternalObjectUpdater)
class _BadgeClassUpdater(object):

    __slots__ = ('obj',)

    def __init__(self, obj):
        self.obj = obj

    def updateFromExternalObject(self, parsed, *args, **kwargs):
        if 'title' not in parsed or not parsed['title']:
            parsed['title'] = parsed.get('description')
        result = InterfaceObjectIO(
                    self.obj,
                    interfaces.IBadgeClass).updateFromExternalObject(parsed)
        return result
