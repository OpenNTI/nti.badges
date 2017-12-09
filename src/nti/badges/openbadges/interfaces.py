#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class

from zope import interface

from zope.interface.interfaces import ObjectEvent
from zope.interface.interfaces import IObjectEvent

from zope.schema import vocabulary

from zope.security.interfaces import IPrincipal

from nti.badges.interfaces import ITaggedContent
from nti.badges.interfaces import IBadgeClass as IBadgeMarker
from nti.badges.interfaces import IBadgeIssuer as IIssuerMarker
from nti.badges.interfaces import IBadgeAssertion as IAssertionMarker

from nti.property.property import alias

from nti.schema.field import Bool
from nti.schema.field import Choice
from nti.schema.field import Object
from nti.schema.field import Variant
from nti.schema.field import ValidText
from nti.schema.field import ListOrTuple
from nti.schema.field import ValidDatetime
from nti.schema.field import DecodingValidTextLine as ValidTextLine

VO_TYPE_HOSTED = u'hosted'
VO_TYPE_SIGNED = u'signed'
VO_TYPES = (VO_TYPE_HOSTED, VO_TYPE_SIGNED)
VO_TYPES_VOCABULARY = \
    vocabulary.SimpleVocabulary([vocabulary.SimpleTerm(_x) for _x in VO_TYPES])

ID_TYPE_EMAIL = u'email'
ID_TYPE_USERNAME = u'username'
ID_TYPES = (ID_TYPE_EMAIL, ID_TYPE_USERNAME)
ID_TYPES_VOCABULARY = \
    vocabulary.SimpleVocabulary([vocabulary.SimpleTerm(_x) for _x in ID_TYPES])


class IVerificationObject(interface.Interface):
    type = Choice(vocabulary=VO_TYPES_VOCABULARY,
                  title=u'Verification method',
                  required=True)
    url = ValidTextLine(
        title=u"URL pointing to the assertion or issuer's public key")


class IIssuerOrganization(IIssuerMarker):
    name = ValidTextLine(title=u"The name of the issuing organization.")

    url = ValidTextLine(title=u'URL of the institution')

    image = ValidTextLine(title=u'Issuer URL logo', required=False)

    email = ValidTextLine(title=u"Issuer email", required=False)

    description = ValidText(title=u"Issuer description", required=False)

    revocationList = ValidTextLine(title=u'Issuer revocations URL',
                                   required=False)


class IIdentityObject(interface.Interface):

    identity = ValidTextLine(title=u"identity hash or text")

    type = Choice(vocabulary=ID_TYPES_VOCABULARY,
                  title=u'The type of identity',
                  required=True, default=ID_TYPE_EMAIL)

    hashed = Bool(title=u'Whether or not the id value is hashed',
                  required=False, default=False)

    salt = ValidTextLine(title=u"Salt string", required=False)


class IAlignmentObject(interface.Interface):

    name = ValidTextLine(title=u"The name of the alignment",
                         required=True)

    url = ValidTextLine(title=u'URL linking to the official description of the standard',
                        required=False)

    description = ValidText(title=u"Short description of the standard",
                            required=False)


class IBadgeClass(ITaggedContent, IBadgeMarker):

    description = ValidText(title=u"A short description of the achievement",
                            required=True)

    image = ValidTextLine(title=u"Image representing the achievement (URL/FileName/DataURI)",
                          required=True)

    criteria = ValidTextLine(title=u'URL of the criteria for earning the achievement',
                             required=False)

    issuer = Variant((ValidTextLine(title=u'URL of the organization that issued the badge'),
                      Object(IIssuerOrganization, title=u"Issuer object")),
                     title=u"Image representing the achievement",
                     required=True)

    alignment = ListOrTuple(value_type=Object(IAlignmentObject),
                            title=u"Objects describing which educational standards",
                            required=False,
                            min_length=0)


class IBadgeAssertion(IAssertionMarker):

    recipient = Object(IIdentityObject,
                       title=u"The recipient of the achievement")

    badge = Variant((Object(IBadgeClass, title=u"Badge class"),
                     ValidTextLine(title=u'Badge URL')),
                    title=u"Badge being awarded")

    verify = Object(IVerificationObject,
                    title=u"Data to help a third party verify this assertion")

    issuedOn = ValidDatetime(title=u"date that the achievement was awarded")

    image = ValidTextLine(title=u"Image representing this user's achievement",
                          required=False)

    evidence = ValidTextLine(title=u'URL of the work that the recipient did to earn the achievement',
                             required=False)

    expires = ValidDatetime(title=u"Achievment expiry", required=False)

    exported = Bool(title=u"If the assertion has been exported", default=False,
                    required=False)
    exported.setTaggedValue('_ext_excluded_out', True)


class IBadgeAwardedEvent(IObjectEvent):
    """
    Interface for an add assertion event
    """
    giver = Object(IPrincipal,
                   title=u"Person giving of the achievement")

    assertion = Object(IBadgeAssertion,
                       title=u"Assertion added")
IBadgeAssertionAddedEvent = IBadgeAwardedEvent


@interface.implementer(IBadgeAwardedEvent)
class BadgeAwardedEvent(ObjectEvent):
    """
    Add assertion event
    """

    giver = alias('creator')
    assertion = alias('object')

    def __init__(self, obj, creator=None):
        ObjectEvent.__init__(self, obj)
        self.creator = creator
BadgeAssertionAddedEvent = BadgeAwardedEvent
