#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope.container import contained

import persistent

from nti.externalization.externalization import make_repr

from nti.utils.schema import SchemaConfigured
from nti.utils.schema import createDirectFieldProperties

from . import interfaces

@interface.implementer(interfaces.INTIBadge)
class NTIBadge(SchemaConfigured, persistent.Persistent, contained.Contained):
    createDirectFieldProperties(interfaces.INTIBadge)

    __external_can_create__ = True
    mime_type = mimeType = 'application/vnd.nextthought.badges.badge'

    def __init__(self, *args, **kwargs):
        persistent.Persistent.__init__(self)
        SchemaConfigured.__init__(self, *args, **kwargs)

    def __eq__(self, other):
        try:
            return self is other or (self.issuer == other.issuer and
                                     self.name == other.name)
        except AttributeError:
            return NotImplemented

    __repr__ = make_repr()

    def __hash__(self):
        xhash = 47
        xhash ^= hash(self.name)
        xhash ^= hash(self.issuer)
        return xhash

@interface.implementer(interfaces.INTIIssuer)
class NTIIssuer(SchemaConfigured, persistent.Persistent, contained.Contained):
    createDirectFieldProperties(interfaces.INTIIssuer)

    __external_can_create__ = True
    mime_type = mimeType = 'application/vnd.nextthought.badges.issuer'

    def __init__(self, *args, **kwargs):
        persistent.Persistent.__init__(self)
        SchemaConfigured.__init__(self, *args, **kwargs)

    def __eq__(self, other):
        try:
            return self is other or (self.uri == other.uri and self.org == other.org)
        except AttributeError:
            return NotImplemented

    __repr__ = make_repr()

    def __hash__(self):
        xhash = 47
        xhash ^= hash(self.uri)
        xhash ^= hash(self.org)
        return xhash

@interface.implementer(interfaces.INTIAssertion)
class NTIAssertion(SchemaConfigured, persistent.Persistent, contained.Contained):
    createDirectFieldProperties(interfaces.INTIAssertion)

    __external_can_create__ = True
    mime_type = mimeType = 'application/vnd.nextthought.badges.assertion'

    def __init__(self, *args, **kwargs):
        persistent.Persistent.__init__(self)
        SchemaConfigured.__init__(self, *args, **kwargs)

    def __eq__(self, other):
        try:
            return self is other or (self.badge == other.badge and
                                     self.recipient == other.recipient and
                                     self.issuedOn == other.issuedOn)
        except AttributeError:
            return NotImplemented

    __repr__ = make_repr()

    def __hash__(self):
        xhash = 47
        xhash ^= hash(self.badge)
        xhash ^= hash(self.issuedOn)
        xhash ^= hash(self.recipient)
        return xhash
