#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface
from zope.schema import vocabulary

from nti.utils import schema as nti_schema

from nti.utils.schema import ValidTextLine
from nti.utils.schema import ValidText
TextLine = ValidTextLine
from nti.utils.schema import ListOrTuple
from nti.utils.schema import Variant
from nti.utils.schema import HTTPURL
from nti.utils.schema import Choice
from nti.utils.schema import Object
from nti.utils.schema import Bool
from nti.utils.schema import DataURI
from nti.utils.schema import ValidDatetime

from .. import interfaces as badge_interfaces

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
	url = Variant((
					TextLine(title='URL assertion/issuer public key'),
					HTTPURL(title='URL assertion/issuer public key')),
					title="URL pointing to the assertion or issuer's public key")


class IIssuerOrganization(badge_interfaces.IBadgeIssuer):
	name = ValidTextLine(title="The name of the issuing organization.")
	url = HTTPURL(title='URL of the institution')
	image = HTTPURL(title='Issuer URL logo', required=False)
	email = ValidTextLine(title="Issuer email", required=False)
	description = ValidText(title="Issuer description", required=False)
	revocationList = HTTPURL(title='Issuer revocations URL', required=False)

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
	url = HTTPURL(title='URL linking to the official description of the standard')
	description = ValidText(title="Short description of the standard",
                                       required=False)

class IBadgeClass(badge_interfaces.ITaggedContent, badge_interfaces.IBadgeClass):
	name = ValidTextLine(title="The name of the achievement")

	description = ValidText(title="A short description of the achievement")

	image = Variant((
					DataURI(title="Image data"),
					HTTPURL(title='Image URL')),
					title="Image representing the achievement")

	criteria = HTTPURL(title='URL of the criteria for earning the achievement')

	issuer = Variant((
					HTTPURL(title='URL of the organization that issued the badge'),
					Object(IIssuerOrganization, title="Issuer object")),
					title="Image representing the achievement")

	alignment = ListOrTuple(value_type=Object(IAlignmentObject),
                                       title="Objects describing which educational standards",
                                       required=False,
                                       min_length=0)

class IBadgeAssertion(badge_interfaces.IBadgeAssertion):
	uid = ValidTextLine(title=" Unique Identifier for the badge")

	recipient = Object(IIdentityObject,
								  title="The recipient of the achievement")
	badge = Variant((
					Object(IBadgeClass, title="Badge class"),
					HTTPURL(title='Badge URL')),
					title="Badge being awarded")

	verify = Object(IVerificationObject,
							   title="Data to help a third party verify this assertion")

	issuedOn = ValidDatetime(title="date that the achievement was awarded")

	image = Variant((
					DataURI(title="Image data"),
					HTTPURL(title='Image URL')),
					title="Image representing this user's achievement",
					required=False)

	evidence = HTTPURL(
					title='URL of the work that the recipient did to earn the achievement',
					required=False)

	expires = ValidDatetime(title="Achievment expiry", required=False)
