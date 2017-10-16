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

from nti.badges.openbadges.interfaces import IBadgeClass
from nti.badges.openbadges.interfaces import IBadgeAssertion
from nti.badges.openbadges.interfaces import IIdentityObject
from nti.badges.openbadges.interfaces import IAlignmentObject
from nti.badges.openbadges.interfaces import IVerificationObject
from nti.badges.openbadges.interfaces import IIssuerOrganization

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
@EqHash('url', 'type')
@six.add_metaclass(MetaBadgeObject)
@interface.implementer(IVerificationObject, IContentTypeAware)
class VerificationObject(SchemaConfigured):
    createDirectFieldProperties(IVerificationObject)

    __external_class_name__ = "Verification"
    mime_type = mimeType = 'application/vnd.nextthought.openbadges.verificationobject'


@WithRepr
@NoPickle
@EqHash('identity', 'type')
@six.add_metaclass(MetaBadgeObject)
@interface.implementer(IIdentityObject, IContentTypeAware)
class IdentityObject(SchemaConfigured):
    createDirectFieldProperties(IIdentityObject)

    __external_class_name__ = "Identity"
    mime_type = mimeType = 'application/vnd.nextthought.openbadges.identityobject'


@WithRepr
@NoPickle
@EqHash('url', 'name')
@six.add_metaclass(MetaBadgeObject)
@interface.implementer(IAlignmentObject, IContentTypeAware)
class AlignmentObject(SchemaConfigured):
    createDirectFieldProperties(IAlignmentObject)

    __external_class_name__ = "Alignment"
    mime_type = mimeType = 'application/vnd.nextthought.openbadges.alignmentobject'


@WithRepr
@NoPickle
@EqHash('name', 'url')
@six.add_metaclass(MetaBadgeObject)
@interface.implementer(IIssuerOrganization, IContentTypeAware)
class IssuerOrganization(SchemaConfigured):
    createDirectFieldProperties(IIssuerOrganization)

    __external_class_name__ = "Issuer"
    mime_type = mimeType = 'application/vnd.nextthought.openbadges.issuer'

    origin = alias('url')
    contact = alias('email')
    issued_on = alias('issuedOn')


@WithRepr
@NoPickle
@EqHash('name')
@six.add_metaclass(MetaBadgeObject)
@interface.implementer(IBadgeClass, IContentTypeAware)
class BadgeClass(SchemaConfigured):
    createDirectFieldProperties(IBadgeClass)

    __external_class_name__ = "Badge"
    mime_type = mimeType = 'application/vnd.nextthought.openbadges.badge'

    def __init__(self, *args, **kwargs):
        if 'tags' in kwargs:
            kwargs['tags'] = IBadgeClass['tags'].fromObject(kwargs['tags'])
        SchemaConfigured.__init__(self, *args, **kwargs)


@WithRepr
@NoPickle
@EqHash('uid', 'recipient')
@six.add_metaclass(MetaBadgeObject)
@interface.implementer(IBadgeAssertion, IContentTypeAware)
class BadgeAssertion(SchemaConfigured):
    createDirectFieldProperties(IBadgeAssertion)

    __external_class_name__ = "Assertion"
    mime_type = mimeType = 'application/vnd.nextthought.openbadges.assertion'

    id = alias('uid')
    locked = alias('exported')
