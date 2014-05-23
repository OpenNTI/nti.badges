#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import time

from zope import component
from zope import interface

from .._compact import navstr

from . import interfaces
from ..model import NTIBadge
from ..model import NTIIssuer
from ..model import NTIPerson
from .. import interfaces as badges_intefaces

@component.adapter(interfaces.IIdentityObject)
@interface.implementer(badges_intefaces.INTIPerson)
def identityobject_to_ntiperson(iio):
    result = NTIPerson(email=iio.identity, name=iio.identity)
    return result

@component.adapter(interfaces.IBadgeClass)
@interface.implementer(badges_intefaces.INTIBadge)
def badgeclass_to_ntibadge(badge):
    issuer = NTIIssuer(uri=navstr(badge.issuer),
                       org=navstr(badge.issuer),
                       origin=navstr(badge.issuer))
    result = NTIBadge(issuer=issuer,
                      id=badge.name,
                      name=badge.name,
                      criteria=navstr(badge.criteria),
                      createdTime=time.time())
    return result
