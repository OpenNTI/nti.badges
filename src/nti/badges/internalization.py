#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

@interface.implementer(ext_interfaces.IInternalObjectUpdater)
class _NTIModelUpdater(object):

    model_interface = None
    def __init__(self, obj):
        self.obj = obj

    def updateFromExternalObject(self, parsed, *args, **kwargs):
        createdTime = parsed.get('CreatedTime', parsed.get('createdTime'))
        result = InterfaceObjectIO(
                    self.obj,
                    self.model_interface).updateFromExternalObject(parsed)
        if createdTime is not None:
            self.obj.createdTime = createdTime
        return result

@interface.implementer(ext_interfaces.IInternalObjectUpdater)
@component.adapter(interfaces.INTIIssuer)
class _NTIIssuerUpdater(_NTIModelUpdater):
    model_interface = interfaces.INTIIssuer

@interface.implementer(ext_interfaces.IInternalObjectUpdater)
@component.adapter(interfaces.INTIBadge)
class _NTIBadgeUpdater(_NTIModelUpdater):
    model_interface = interfaces.INTIBadge

@interface.implementer(ext_interfaces.IInternalObjectUpdater)
@component.adapter(interfaces.INTIPerson)
class _NTIPersonUpdater(_NTIModelUpdater):
    model_interface = interfaces.INTIPerson
