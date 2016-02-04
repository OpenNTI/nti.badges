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

from nti.common.persistence import NoPickle

from nti.common.property import alias

from nti.common.representation import WithRepr

from nti.badges.interfaces import INTIBadge
from nti.badges.interfaces import INTIIssuer
from nti.badges.interfaces import INTIPerson
from nti.badges.interfaces import INTIAssertion

from nti.badges.utils import MetaBadgeObject

from nti.schema.field import SchemaConfigured
from nti.schema.fieldproperty import createDirectFieldProperties

from nti.schema.schema import EqHash

@WithRepr
@NoPickle
@EqHash('issuer', 'name')
@interface.implementer(INTIBadge, IContentTypeAware)
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

@WithRepr
@NoPickle
@EqHash('name', 'email')
@interface.implementer(INTIPerson, IContentTypeAware)
class NTIPerson(SchemaConfigured):
	__metaclass__ = MetaBadgeObject
	createDirectFieldProperties(INTIPerson)

	__external_class_name__ = "Person"
	mime_type = mimeType = 'application/vnd.nextthought.badges.person'

@WithRepr
@NoPickle
@EqHash('name', 'origin')
@interface.implementer(INTIIssuer, IContentTypeAware)
class NTIIssuer(SchemaConfigured):
	__metaclass__ = MetaBadgeObject
	createDirectFieldProperties(INTIIssuer)

	__external_can_create__ = True
	__external_class_name__ = "Issuer"
	mime_type = mimeType = 'application/vnd.nextthought.badges.issuer'

	org = alias('organization')

@WithRepr
@NoPickle
@EqHash('badge', 'recipient', 'issuedOn')
@interface.implementer(INTIAssertion, IContentTypeAware)
class NTIAssertion(SchemaConfigured):
	__metaclass__ = MetaBadgeObject
	createDirectFieldProperties(INTIAssertion)

	__external_class_name__ = "Assertion"
	mime_type = mimeType = 'application/vnd.nextthought.badges.assertion'

	id = alias('uid')
	locked = alias('exported')
