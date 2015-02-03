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

from .interfaces import INTIBadge
from .interfaces import INTIIssuer
from .interfaces import INTIPerson
from .interfaces import INTIAssertion

@interface.implementer(INTIBadge)
@WithRepr
@NoPickle
@EqHash('issuer', 'name')
class NTIBadge(SchemaConfigured, Contained):
	createFieldProperties(INTIBadge)

	__external_can_create__ = True
	__external_class_name__ = "Badge"
	mime_type = mimeType = 'application/vnd.nextthought.badges.badge'

	id = alias('name')

	def __init__(self, *args, **kwargs):
		if 'tags' in kwargs:
			kwargs['tags'] = INTIBadge['tags'].fromObject(kwargs['tags'])
		SchemaConfigured.__init__(self, *args, **kwargs)

@interface.implementer(INTIPerson)
@WithRepr
@NoPickle
@EqHash('name', 'email')
class NTIPerson(SchemaConfigured, Contained):
	createFieldProperties(INTIPerson)

	__external_can_create__ = True
	__external_class_name__ = "Person"
	mime_type = mimeType = 'application/vnd.nextthought.badges.person'

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)

@interface.implementer(INTIIssuer)
@WithRepr
@NoPickle
@EqHash('name', 'origin')
class NTIIssuer(SchemaConfigured, Contained):
	createFieldProperties(INTIIssuer)

	__external_can_create__ = True
	__external_class_name__ = "Issuer"
	mime_type = mimeType = 'application/vnd.nextthought.badges.issuer'

	org = alias('organization')

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)

@interface.implementer(INTIAssertion)
@WithRepr
@NoPickle
@EqHash('badge', 'recipient', 'issuedOn')
class NTIAssertion(SchemaConfigured, Contained):
	createFieldProperties(INTIAssertion)

	__external_can_create__ = True
	__external_class_name__ = "Assertion"
	mime_type = mimeType = 'application/vnd.nextthought.badges.assertion'

	id = alias('uid')

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)
