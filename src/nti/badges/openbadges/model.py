#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from .interfaces import IBadgeClass

@interface.implementer(interfaces.IVerificationObject)
class VerificationObject(SchemaConfigured, persistent.Persistent, contained.Contained):
	createFieldProperties(interfaces.IVerificationObject)

	__external_can_create__ = True
	__external_class_name__ = "Verification"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.verificationobject'

	def __init__(self, *args, **kwargs):
		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

	def __eq__(self, other):
		try:
			return self is other or (self.type == other.type and self.url == other.url)
		except AttributeError:
			return NotImplemented

	__repr__ = make_repr()

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.url)
		xhash ^= hash(self.type)
		return xhash

@interface.implementer(interfaces.IIdentityObject)
class IdentityObject(SchemaConfigured, persistent.Persistent, contained.Contained):
	createFieldProperties(interfaces.IIdentityObject)

	__external_can_create__ = True
	__external_class_name__ = "Identity"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.identityobject'

	def __init__(self, *args, **kwargs):
		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

	def __eq__(self, other):
		try:
			return self is other or (self.identity == other.identity
									 and self.type == other.type)
		except AttributeError:
			return NotImplemented

	__repr__ = make_repr()

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.type)
		xhash ^= hash(self.identity)
		return xhash

@interface.implementer(interfaces.IAlignmentObject)
class AlignmentObject(SchemaConfigured, persistent.Persistent, contained.Contained):
	createFieldProperties(interfaces.IAlignmentObject)

	__external_can_create__ = True
	__external_class_name__ = "Alignment"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.alignmentobject'

	def __init__(self, *args, **kwargs):
		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

	def __eq__(self, other):
		try:
			return self is other or (self.name == other.name and self.url == other.url)
		except AttributeError:
			return NotImplemented

	__repr__ = make_repr()

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.url)
		xhash ^= hash(self.name)
		return xhash

@interface.implementer(interfaces.IIssuerOrganization)
class IssuerOrganization(SchemaConfigured, persistent.Persistent, contained.Contained):
	createFieldProperties(interfaces.IIssuerOrganization)

	__external_can_create__ = True
	__external_class_name__ = "Issuer"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.issuer'

	origin = alias('url')
	contact = alias('email')
	issued_on = alias('issuedOn')

	def __init__(self, *args, **kwargs):
		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

	def __eq__(self, other):
		try:
			return self is other or (self.name == other.name and self.url == other.url)
		except AttributeError:
			return NotImplemented

	__repr__ = make_repr()

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.url)
		xhash ^= hash(self.name)
		return xhash

@interface.implementer(IBadgeClass)
class BadgeClass(SchemaConfigured, persistent.Persistent, contained.Contained):
	createFieldProperties(IBadgeClass)

	__external_can_create__ = True
	__external_class_name__ = "Badge"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.badge'

	def __init__(self, *args, **kwargs):
		if 'tags' in kwargs:
			kwargs['tags'] = IBadgeClass['tags'].fromObject(kwargs['tags'])

		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

	def __eq__(self, other):
		try:
			return self is other or (self.name == other.name)
		except AttributeError:
			return NotImplemented

	__repr__ = make_repr()

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.name)
		return xhash

@interface.implementer(interfaces.IBadgeAssertion)
class BadgeAssertion(SchemaConfigured, persistent.Persistent, contained.Contained):
	createFieldProperties(interfaces.IBadgeAssertion)

	__external_can_create__ = True
	__external_class_name__ = "Assertion"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.assertion'

	def __init__(self, *args, **kwargs):
		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

	def __eq__(self, other):
		try:
			return self is other or (self.uid == other.uid
									 and self.recipient == other.recipient)
		except AttributeError:
			return NotImplemented

	__repr__ = make_repr()

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.uid)
		xhash ^= hash(self.recipient)
		return xhash
