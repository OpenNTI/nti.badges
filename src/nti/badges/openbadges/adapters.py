#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from . import interfaces
from ..model import NTIPerson
from .. import interfaces as badges_intefaces

@component.adapter(interfaces.IIdentityObject)
@interface.implementer(badges_intefaces.INTIPerson)
def identityobject_to_ntiperson(iio):
    result = NTIPerson(email=iio.identity, name=iio.identity)
    return result
