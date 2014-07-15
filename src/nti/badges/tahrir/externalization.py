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

from nti.externalization.interfaces import IExternalObject
from nti.externalization.externalization import to_external_object

from ..openbadges.interfaces import IBadgeClass
from ..openbadges.interfaces import IIssuerOrganization

from .interfaces import IBadge
from .interfaces import IIssuer

@interface.implementer(IExternalObject)
@component.adapter(IBadge)
class _BadgeExternalizer(object):

	__slots__ = ('badge',)

	def __init__(self, badge):
		self.badge = badge

	def toExternalObject(self, *args, **kwargs):
		return to_external_object(IBadgeClass(self.badge))
	
@interface.implementer(IExternalObject)
@component.adapter(IIssuer)
class _IssuerExternalizer(object):

	__slots__ = ('issuer',)

	def __init__(self, issuer):
		self.issuer = issuer

	def toExternalObject(self, *args, **kwargs):
		return to_external_object(IIssuerOrganization(self.issuer))

