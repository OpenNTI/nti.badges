#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from zope.mimetype.interfaces import IContentTypeAware

from nti.common.property import alias

from nti.externalization.persistence import NoPickle
from nti.externalization.representation import WithRepr

from nti.schema.schema import EqHash
from nti.schema.field import SchemaConfigured
from nti.schema.fieldproperty import createDirectFieldProperties

from ..utils import MetaBadgeObject

from .interfaces import IBadgeClass
from .interfaces import IBadgeAssertion
from .interfaces import IIdentityObject
from .interfaces import IAlignmentObject
from .interfaces import IVerificationObject
from .interfaces import IIssuerOrganization

@interface.implementer(IVerificationObject, IContentTypeAware)
@WithRepr
@NoPickle
@EqHash('url', 'type')
class VerificationObject(SchemaConfigured):
	__metaclass__ = MetaBadgeObject
	createDirectFieldProperties(IVerificationObject)

	__external_class_name__ = "Verification"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.verificationobject'

@interface.implementer(IIdentityObject, IContentTypeAware)
@WithRepr
@NoPickle
@EqHash('identity', 'type')
class IdentityObject(SchemaConfigured):
	__metaclass__ = MetaBadgeObject
	createDirectFieldProperties(IIdentityObject)

	__external_class_name__ = "Identity"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.identityobject'

@interface.implementer(IAlignmentObject, IContentTypeAware)
@WithRepr
@NoPickle
@EqHash('url', 'name')
class AlignmentObject(SchemaConfigured):
	__metaclass__ = MetaBadgeObject
	createDirectFieldProperties(IAlignmentObject)

	__external_class_name__ = "Alignment"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.alignmentobject'

@interface.implementer(IIssuerOrganization, IContentTypeAware)
@WithRepr
@NoPickle
@EqHash('name', 'url')
class IssuerOrganization(SchemaConfigured):
	__metaclass__ = MetaBadgeObject
	createDirectFieldProperties(IIssuerOrganization)

	__external_class_name__ = "Issuer"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.issuer'

	origin = alias('url')
	contact = alias('email')
	issued_on = alias('issuedOn')

@interface.implementer(IBadgeClass, IContentTypeAware)
@WithRepr
@NoPickle
@EqHash('name')
class BadgeClass(SchemaConfigured):
	__metaclass__ = MetaBadgeObject
	createDirectFieldProperties(IBadgeClass)

	__external_class_name__ = "Badge"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.badge'

	def __init__(self, *args, **kwargs):
		if 'tags' in kwargs:
			kwargs['tags'] = IBadgeClass['tags'].fromObject(kwargs['tags'])
		SchemaConfigured.__init__(self, *args, **kwargs)

@interface.implementer(IBadgeAssertion, IContentTypeAware)
@WithRepr
@NoPickle
@EqHash('uid', 'recipient')
class BadgeAssertion(SchemaConfigured):
	__metaclass__ = MetaBadgeObject
	createDirectFieldProperties(IBadgeAssertion)

	__external_class_name__ = "Assertion"
	mime_type = mimeType = 'application/vnd.nextthought.openbadges.assertion'

	id = alias('uid')
