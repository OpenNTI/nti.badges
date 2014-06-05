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

from nti.utils.property import alias
from nti.utils.schema import SchemaConfigured
from nti.utils.schema import createFieldProperties
# NOTE: None of these classes are inheriting from other
# schema-configured classes, so we MUST create all the field
# properties; only when inheritance is involved should we
# create just the direct field properties
#from nti.utils.schema import createDirectFieldProperties

from . import interfaces
from .interfaces import INTIBadge

# XXX: JAM: Why are these persistent? We don't expect them to be
# stored in the ZODB anywhere do we?

@interface.implementer(INTIBadge)
class NTIBadge(SchemaConfigured, persistent.Persistent, contained.Contained):
	createFieldProperties(INTIBadge)

	__external_can_create__ = True
	__external_class_name__ = "Badge"
	mime_type = mimeType = 'application/vnd.nextthought.badges.badge'

	id = alias('name')

	def __init__(self, *args, **kwargs):
		if 'tags' in kwargs:
			kwargs['tags'] = INTIBadge['tags'].fromObject(kwargs['tags'])
		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

	def __eq__(self, other):
		try:
			return self is other or (self.issuer == other.issuer
									 and self.name == other.name)
		except AttributeError:
			return NotImplemented

	__repr__ = make_repr()

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.name)
		xhash ^= hash(self.issuer)
		return xhash

@interface.implementer(interfaces.INTIPerson)
class NTIPerson(SchemaConfigured, persistent.Persistent, contained.Contained):
	createFieldProperties(interfaces.INTIPerson)

	__external_can_create__ = True
	__external_class_name__ = "Person"
	mime_type = mimeType = 'application/vnd.nextthought.badges.person'

	def __init__(self, *args, **kwargs):
		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

	def __eq__(self, other):
		try:
			return self is other or (self.name == other.name and
									 self.email == other.email)
		except AttributeError:
			return NotImplemented

	__repr__ = make_repr()

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.name)
		xhash ^= hash(self.email)
		return xhash

@interface.implementer(interfaces.INTIIssuer)
class NTIIssuer(SchemaConfigured, persistent.Persistent, contained.Contained):
	createFieldProperties(interfaces.INTIIssuer)

	__external_can_create__ = True
	__external_class_name__ = "Issuer"
	mime_type = mimeType = 'application/vnd.nextthought.badges.issuer'

	org = alias('organization')

	def __init__(self, *args, **kwargs):
		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

	def __eq__(self, other):
		try:
			return self is other or (self.name == other.name and
									 self.origin == other.origin)
		except AttributeError:
			return NotImplemented

	__repr__ = make_repr()

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.name)
		xhash ^= hash(self.origin)
		return xhash

@interface.implementer(interfaces.INTIAssertion)
class NTIAssertion(SchemaConfigured, persistent.Persistent, contained.Contained):
	createFieldProperties(interfaces.INTIAssertion)

	__external_can_create__ = True
	__external_class_name__ = "Assertion"
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
