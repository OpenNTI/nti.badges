#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope.container.contained import Contained

from nti.externalization.persistence import NoPickle
from nti.externalization.representation import WithRepr

from nti.common.property import alias

from nti.schema.schema import EqHash
from nti.schema.field import SchemaConfigured
from nti.schema.fieldproperty import createFieldProperties

# NOTE: None of these classes are inheriting from other
# schema-configured classes, so we MUST create all the field
# properties; only when inheritance is involved should we
# create just the direct field properties
# from nti.schema.fieldproperty import createDirectFieldProperties

from .interfaces import IBadgeClass
from .interfaces import IBadgeAssertion
from .interfaces import IIdentityObject
from .interfaces import IAlignmentObject
from .interfaces import IVerificationObject
from .interfaces import IIssuerOrganization

@interface.implementer(IVerificationObject)
@WithRepr
@NoPickle
@EqHash('url', 'type')
class VerificationObject(SchemaConfigured, Contained):
	createFieldProperties(IVerificationObject)

	__external_can_create__ = True
	__external_class_name__ = "Verification"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.verificationobject'

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)

@interface.implementer(IIdentityObject)
@WithRepr
@NoPickle
@EqHash('identity', 'type')
class IdentityObject(SchemaConfigured, Contained):
	createFieldProperties(IIdentityObject)

	__external_can_create__ = True
	__external_class_name__ = "Identity"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.identityobject'

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)

@interface.implementer(IAlignmentObject)
@WithRepr
@NoPickle
@EqHash('url', 'name')
class AlignmentObject(SchemaConfigured, Contained):
	createFieldProperties(IAlignmentObject)

	__external_can_create__ = True
	__external_class_name__ = "Alignment"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.alignmentobject'

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)

@interface.implementer(IIssuerOrganization)
@WithRepr
@NoPickle
@EqHash('name', 'url')
class IssuerOrganization(SchemaConfigured, Contained):
	createFieldProperties(IIssuerOrganization)

	__external_can_create__ = True
	__external_class_name__ = "Issuer"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.issuer'

	origin = alias('url')
	contact = alias('email')
	issued_on = alias('issuedOn')

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)

@interface.implementer(IBadgeClass)
@WithRepr
@NoPickle
@EqHash('name')
class BadgeClass(SchemaConfigured, Contained):
	createFieldProperties(IBadgeClass)

	__external_can_create__ = True
	__external_class_name__ = "Badge"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.badge'

	def __init__(self, *args, **kwargs):
		if 'tags' in kwargs:
			kwargs['tags'] = IBadgeClass['tags'].fromObject(kwargs['tags'])

		SchemaConfigured.__init__(self, *args, **kwargs)

@interface.implementer(IBadgeAssertion)
@WithRepr
@NoPickle
@EqHash('uid', 'recipient')
class BadgeAssertion(SchemaConfigured, Contained):
	createFieldProperties(IBadgeAssertion)

	__external_can_create__ = True
	__external_class_name__ = "Assertion"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.assertion'

	id = alias('uid')

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)
