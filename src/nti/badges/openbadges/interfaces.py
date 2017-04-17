#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface

from zope.interface.interfaces import ObjectEvent
from zope.interface.interfaces import IObjectEvent

from zope.schema import vocabulary

from nti.badges.interfaces import ITaggedContent
from nti.badges.interfaces import IBadgeClass as IBadgeMarker
from nti.badges.interfaces import IBadgeIssuer as IIssuerMarker
from nti.badges.interfaces import IBadgeAssertion as IAssertionMarker

from nti.schema.field import Bool
from nti.schema.field import Choice
from nti.schema.field import Object
from nti.schema.field import Variant
from nti.schema.field import ValidText
from nti.schema.field import ListOrTuple
from nti.schema.field import ValidDatetime
from nti.schema.field import DecodingValidTextLine as ValidTextLine

VO_TYPE_HOSTED = 'hosted'
VO_TYPE_SIGNED = 'signed'
VO_TYPES = (VO_TYPE_HOSTED, VO_TYPE_SIGNED)
VO_TYPES_VOCABULARY = \
    vocabulary.SimpleVocabulary([vocabulary.SimpleTerm(_x) for _x in VO_TYPES])

ID_TYPE_EMAIL = 'email'
ID_TYPE_USERNAME = 'username'
ID_TYPES = (ID_TYPE_EMAIL, ID_TYPE_USERNAME)
ID_TYPES_VOCABULARY = \
    vocabulary.SimpleVocabulary([vocabulary.SimpleTerm(_x) for _x in ID_TYPES])


class IVerificationObject(interface.Interface):
    type = Choice(vocabulary=VO_TYPES_VOCABULARY,
                  title='Verification method',
                  required=True)
    url = ValidTextLine(
        title="URL pointing to the assertion or issuer's public key")


class IIssuerOrganization(IIssuerMarker):
    name = ValidTextLine(title="The name of the issuing organization.")
    url = ValidTextLine(title='URL of the institution')
    image = ValidTextLine(title='Issuer URL logo', required=False)
    email = ValidTextLine(title="Issuer email", required=False)
    description = ValidText(title="Issuer description", required=False)
    revocationList = ValidTextLine(title='Issuer revocations URL', 
                                   required=False)


class IIdentityObject(interface.Interface):
    identity = ValidTextLine(title="identity hash or text")

    type = Choice(vocabulary=ID_TYPES_VOCABULARY,
                  title='The type of identity',
                  required=True, default=ID_TYPE_EMAIL)

    hashed = Bool(title='Whether or not the id value is hashed',
                  required=False, default=False)

    salt = ValidTextLine(title="Salt string", required=False)


class IAlignmentObject(interface.Interface):
    name = ValidTextLine(title="The name of the alignment")
    url = ValidTextLine(
        title='URL linking to the official description of the standard')
    description = ValidText(title="Short description of the standard",
                            required=False)


class IBadgeClass(ITaggedContent, IBadgeMarker):

    description = ValidText(title="A short description of the achievement")

    image = ValidTextLine(
        title="Image representing the achievement (URL/FileName/DataURI)")

    criteria = ValidTextLine(
        title='URL of the criteria for earning the achievement')

    issuer = Variant((ValidTextLine(title='URL of the organization that issued the badge'),
                      Object(IIssuerOrganization, title="Issuer object")),
                     title="Image representing the achievement")

    alignment = ListOrTuple(value_type=Object(IAlignmentObject),
                            title="Objects describing which educational standards",
                            required=False,
                            min_length=0)


class IBadgeAssertion(IAssertionMarker):

    recipient = Object(IIdentityObject, 
                       title="The recipient of the achievement")

    badge = Variant((
        Object(IBadgeClass, title="Badge class"),
        ValidTextLine(title='Badge URL')),
        title="Badge being awarded")

    verify = Object(IVerificationObject,
                    title="Data to help a third party verify this assertion")

    issuedOn = ValidDatetime(title="date that the achievement was awarded")

    image = ValidTextLine(
        title="Image representing this user's achievement", required=False)

    evidence = ValidTextLine(title='URL of the work that the recipient did to earn the achievement',
                             required=False)

    expires = ValidDatetime(title="Achievment expiry", required=False)

    exported = Bool(title="If the assertion has been exported", default=False,
                    required=False)
    exported.setTaggedValue('_ext_excluded_out', True)


class IBadgeAwardedEvent(IObjectEvent):
    pass


@interface.implementer(IBadgeAwardedEvent)
class BadgeAwardedEvent(ObjectEvent):
    pass
