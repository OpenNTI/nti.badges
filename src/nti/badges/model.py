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

from .utils import MetaBadgeObject

from .interfaces import INTIBadge
from .interfaces import INTIIssuer
from .interfaces import INTIPerson
from .interfaces import INTIAssertion

@interface.implementer(INTIBadge, IContentTypeAware)
@WithRepr
@NoPickle
@EqHash('issuer', 'name')
class NTIBadge(SchemaConfigured):
	__metaclass__ = MetaBadgeObject
	createDirectFieldProperties(INTIBadge)

	__external_class_name__ = "Badge"
	mime_type = mimeType = 'application/vnd.nextthought.badges.badge'

	id = alias('name')

	def __init__(self, *args, **kwargs):
		if 'tags' in kwargs:
			kwargs['tags'] = INTIBadge['tags'].fromObject(kwargs['tags'])
		SchemaConfigured.__init__(self, *args, **kwargs)

@interface.implementer(INTIPerson, IContentTypeAware)
@WithRepr
@NoPickle
@EqHash('name', 'email')
class NTIPerson(SchemaConfigured):
	__metaclass__ = MetaBadgeObject
	createDirectFieldProperties(INTIPerson)

	__external_class_name__ = "Person"
	mime_type = mimeType = 'application/vnd.nextthought.badges.person'

@interface.implementer(INTIIssuer, IContentTypeAware)
@WithRepr
@NoPickle
@EqHash('name', 'origin')
class NTIIssuer(SchemaConfigured):
	__metaclass__ = MetaBadgeObject
	createDirectFieldProperties(INTIIssuer)

	__external_can_create__ = True
	__external_class_name__ = "Issuer"
	mime_type = mimeType = 'application/vnd.nextthought.badges.issuer'

	org = alias('organization')

@interface.implementer(INTIAssertion, IContentTypeAware)
@WithRepr
@NoPickle
@EqHash('badge', 'recipient', 'issuedOn')
class NTIAssertion(SchemaConfigured):
	__metaclass__ = MetaBadgeObject
	createDirectFieldProperties(INTIAssertion)

	__external_class_name__ = "Assertion"
	mime_type = mimeType = 'application/vnd.nextthought.badges.assertion'

	id = alias('uid')
	locked = alias('exported')
