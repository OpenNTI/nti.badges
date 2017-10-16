#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import six

from zope import interface

from zope.mimetype.interfaces import IContentTypeAware

from nti.badges.interfaces import INTIBadge
from nti.badges.interfaces import INTIIssuer
from nti.badges.interfaces import INTIPerson
from nti.badges.interfaces import INTIAssertion

from nti.badges.utils import MetaBadgeObject

from nti.externalization.persistence import NoPickle

from nti.externalization.representation import WithRepr

from nti.property.property import alias

from nti.schema.eqhash import EqHash

from nti.schema.field import SchemaConfigured

from nti.schema.fieldproperty import createDirectFieldProperties

logger = __import__('logging').getLogger(__name__)


@WithRepr
@NoPickle
@EqHash('issuer', 'name')
@six.add_metaclass(MetaBadgeObject)
@interface.implementer(INTIBadge, IContentTypeAware)
class NTIBadge(SchemaConfigured):
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
@six.add_metaclass(MetaBadgeObject)
@interface.implementer(INTIPerson, IContentTypeAware)
class NTIPerson(SchemaConfigured):
    createDirectFieldProperties(INTIPerson)

    __external_class_name__ = "Person"
    mime_type = mimeType = 'application/vnd.nextthought.badges.person'


@WithRepr
@NoPickle
@EqHash('name', 'origin')
@six.add_metaclass(MetaBadgeObject)
@interface.implementer(INTIIssuer, IContentTypeAware)
class NTIIssuer(SchemaConfigured):
    createDirectFieldProperties(INTIIssuer)

    __external_can_create__ = True
    __external_class_name__ = "Issuer"
    mime_type = mimeType = 'application/vnd.nextthought.badges.issuer'

    org = alias('organization')


@WithRepr
@NoPickle
@six.add_metaclass(MetaBadgeObject)
@EqHash('badge', 'recipient', 'issuedOn')
@interface.implementer(INTIAssertion, IContentTypeAware)
class NTIAssertion(SchemaConfigured):
    createDirectFieldProperties(INTIAssertion)

    __external_class_name__ = "Assertion"
    mime_type = mimeType = 'application/vnd.nextthought.badges.assertion'

    id = alias('uid')
    locked = alias('exported')
