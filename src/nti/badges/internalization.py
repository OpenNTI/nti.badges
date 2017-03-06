#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from nti.badges.interfaces import INTIBadge
from nti.badges.interfaces import INTIIssuer
from nti.badges.interfaces import INTIPerson

from nti.externalization.datastructures import InterfaceObjectIO

from nti.externalization.interfaces import IInternalObjectUpdater
from nti.externalization.interfaces import StandardExternalFields
from nti.externalization.interfaces import StandardInternalFields


@interface.implementer(IInternalObjectUpdater)
class _NTIModelUpdater(object):

    model_interface = None

    def __init__(self, obj):
        self.obj = obj

    def updateFromExternalObject(self, parsed, *args, **kwargs):
        createdTime = parsed.get(StandardExternalFields.CREATED_TIME) \
                   or parsed.get(StandardInternalFields.CREATED_TIME)
        result = InterfaceObjectIO(
                    self.obj,
                    self.model_interface).updateFromExternalObject(parsed)
        if createdTime is not None:
            self.obj.createdTime = createdTime
        return result


@interface.implementer(IInternalObjectUpdater)
@component.adapter(INTIIssuer)
class _NTIIssuerUpdater(_NTIModelUpdater):
    model_interface = INTIIssuer


@interface.implementer(IInternalObjectUpdater)
@component.adapter(INTIBadge)
class _NTIBadgeUpdater(_NTIModelUpdater):
    model_interface = INTIBadge


@interface.implementer(IInternalObjectUpdater)
@component.adapter(INTIPerson)
class _NTIPersonUpdater(_NTIModelUpdater):
    model_interface = INTIPerson
