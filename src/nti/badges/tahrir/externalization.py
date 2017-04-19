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

from nti.badges.openbadges.interfaces import IBadgeClass
from nti.badges.openbadges.interfaces import IIssuerOrganization

from nti.badges.tahrir.interfaces import IBadge
from nti.badges.tahrir.interfaces import IIssuer

from nti.externalization.externalization import to_external_object

from nti.externalization.interfaces import IExternalObject


@component.adapter(IBadge)
@interface.implementer(IExternalObject)
class _BadgeExternalizer(object):

    __slots__ = ('badge',)

    def __init__(self, badge):
        self.badge = badge

    def toExternalObject(self, *args, **kwargs):
        return to_external_object(IBadgeClass(self.badge))


@component.adapter(IIssuer)
@interface.implementer(IExternalObject)
class _IssuerExternalizer(object):

    __slots__ = ('issuer',)

    def __init__(self, issuer):
        self.issuer = issuer

    def toExternalObject(self, *args, **kwargs):
        return to_external_object(IIssuerOrganization(self.issuer))
