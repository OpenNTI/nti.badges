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

from nti.externalization.externalization import WithRepr
from nti.externalization.externalization import NoPickle

from nti.utils.property import alias

from nti.schema.schema import EqHash
from nti.schema.field import SchemaConfigured
from nti.schema.fieldproperty import createFieldProperties

# NOTE: None of these classes are inheriting from other
# schema-configured classes, so we MUST create all the field
# properties; only when inheritance is involved should we
# create just the direct field properties
# from nti.utils.schema import createDirectFieldProperties

from . import interfaces
from .interfaces import IBadgeClass

@interface.implementer(interfaces.IVerificationObject)
@WithRepr
@NoPickle
@EqHash('url', 'type')
class VerificationObject(SchemaConfigured,
						 contained.Contained):
	createFieldProperties(interfaces.IVerificationObject)

	__external_can_create__ = True
	__external_class_name__ = "Verification"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.verificationobject'

	def __init__(self, *args, **kwargs):
		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

@interface.implementer(interfaces.IIdentityObject)
@WithRepr
@NoPickle
@EqHash('identity', 'type')
class IdentityObject(SchemaConfigured,
					 contained.Contained):
	createFieldProperties(interfaces.IIdentityObject)

	__external_can_create__ = True
	__external_class_name__ = "Identity"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.identityobject'

	def __init__(self, *args, **kwargs):
		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

@interface.implementer(interfaces.IAlignmentObject)
@WithRepr
@NoPickle
@EqHash('url', 'name')
class AlignmentObject(SchemaConfigured,
					  contained.Contained):
	createFieldProperties(interfaces.IAlignmentObject)

	__external_can_create__ = True
	__external_class_name__ = "Alignment"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.alignmentobject'

	def __init__(self, *args, **kwargs):
		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

@interface.implementer(interfaces.IIssuerOrganization)
@WithRepr
@NoPickle
@EqHash('name', 'url')
class IssuerOrganization(SchemaConfigured,
						 contained.Contained):
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

@interface.implementer(IBadgeClass)
@WithRepr
@NoPickle
@EqHash('name')
class BadgeClass(SchemaConfigured,
				 contained.Contained):
	createFieldProperties(IBadgeClass)

	__external_can_create__ = True
	__external_class_name__ = "Badge"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.badge'

	def __init__(self, *args, **kwargs):
		if 'tags' in kwargs:
			kwargs['tags'] = IBadgeClass['tags'].fromObject(kwargs['tags'])

		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

@interface.implementer(interfaces.IBadgeAssertion)
@WithRepr
@NoPickle
@EqHash('uid', 'recipient')
class BadgeAssertion(SchemaConfigured,
					 contained.Contained):
	createFieldProperties(interfaces.IBadgeAssertion)

	__external_can_create__ = True
	__external_class_name__ = "Assertion"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.assertion'

	id = alias('uid')

	def __init__(self, *args, **kwargs):
		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)
