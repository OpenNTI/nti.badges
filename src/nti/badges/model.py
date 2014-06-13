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

from nti.externalization.externalization import WithRepr
from nti.externalization.externalization import NoPickle

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

from nti.utils.schema import EqHash as _EqHash

@interface.implementer(INTIBadge)
@WithRepr
@NoPickle
@_EqHash('issuer', 'name')
class NTIBadge(SchemaConfigured,
			   contained.Contained):
	createFieldProperties(INTIBadge)

	__external_can_create__ = True
	__external_class_name__ = "Badge"
	mime_type = mimeType = 'application/vnd.nextthought.badges.badge'

	id = alias('name')

	def __init__(self, *args, **kwargs):
		if 'tags' in kwargs:
			kwargs['tags'] = INTIBadge['tags'].fromObject(kwargs['tags'])
		SchemaConfigured.__init__(self, *args, **kwargs)

@interface.implementer(interfaces.INTIPerson)
@WithRepr
@NoPickle
@_EqHash('name', 'email')
class NTIPerson(SchemaConfigured,
				contained.Contained):
	createFieldProperties(interfaces.INTIPerson)

	__external_can_create__ = True
	__external_class_name__ = "Person"
	mime_type = mimeType = 'application/vnd.nextthought.badges.person'

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)

@interface.implementer(interfaces.INTIIssuer)
@WithRepr
@NoPickle
@_EqHash('name', 'origin')
class NTIIssuer(SchemaConfigured,
				contained.Contained):
	createFieldProperties(interfaces.INTIIssuer)

	__external_can_create__ = True
	__external_class_name__ = "Issuer"
	mime_type = mimeType = 'application/vnd.nextthought.badges.issuer'

	org = alias('organization')

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)

@interface.implementer(interfaces.INTIAssertion)
@WithRepr
@NoPickle
@_EqHash('badge', 'recipient', 'issuedOn')
class NTIAssertion(SchemaConfigured,
				   contained.Contained):
	createFieldProperties(interfaces.INTIAssertion)

	__external_can_create__ = True
	__external_class_name__ = "Assertion"
	mime_type = mimeType = 'application/vnd.nextthought.badges.assertion'

	id = alias('uid')

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)
