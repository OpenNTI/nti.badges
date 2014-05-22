#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.utils.schema import AdaptingFieldProperty
from nti.utils.schema import createDirectFieldProperties

from . import interfaces
from ..model import NTIBadge
from ..model import NTIIssuer
from ..model import NTIAssertion

@interface.implementer(interfaces.ITahrirBadge)
class TahrirBadge(NTIBadge):
    createDirectFieldProperties(interfaces.ITahrirBadge)
    data = AdaptingFieldProperty(interfaces.ITahrirBadge['data'])
    mime_type = mimeType = 'application/vnd.nextthought.tahrir.badge'

@interface.implementer(interfaces.ITahrirIssuer)
class TahrirIssuer(NTIIssuer):
    createDirectFieldProperties(interfaces.ITahrirBadge)
    mime_type = mimeType = 'application/vnd.nextthought.tahrir.issuer'

@interface.implementer(interfaces.ITahrirAssertion)
class TahrirAssertion(NTIAssertion):
    createDirectFieldProperties(interfaces.ITahrirAssertion)
    badge = AdaptingFieldProperty(interfaces.ITahrirAssertion['badge'])
    mime_type = mimeType = 'application/vnd.nextthought.tahrir.assertion'
