#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface

from nti.schema.field import Int
from nti.schema.field import Bool
from nti.schema.field import ValidText
from nti.schema.field import ValidDatetime
from nti.schema.field import DecodingValidTextLine as ValidTextLine

from ..interfaces import IBadgeClass
from ..interfaces import IBadgeIssuer
from ..interfaces import IBadgeManager
from ..interfaces import IBadgeAssertion

class ITahrirModel(interface.Interface):
	"""
	marker interface for Tahrir model objects
	"""

class IIssuer(ITahrirModel, IBadgeIssuer):
	id = Int(title=" Issuer id")
	origin = ValidTextLine(title="Issuer origin")
	name = ValidTextLine(title=" Issuer name")
	org = ValidTextLine(title=" Issuer organization")
	contact = ValidTextLine(title=" Issuer contact")
	created_on =  ValidDatetime(title="Created time")

class IBadge(ITahrirModel, IBadgeClass):
	name = ValidTextLine(title="Badge name")

	image = ValidTextLine(title="Image name/URL")

	description = ValidText(title="Badge description")

	criteria = ValidTextLine(title="Criteria URL")

	issuer_id = Int(title='Issuer id')

	created_on =  ValidDatetime(title="Created time")

	tags = ValidTextLine(title=" Badge tags")

class IPerson(ITahrirModel):
	id = Int(title="Person's id")

	email = ValidTextLine(title=" Person's email")

	nickname = ValidTextLine(title=" Person's nickname", required=False)

	website = ValidTextLine(title="Image name/URL")

	bio = ValidText(title="Person's bio", required=False)

	created_on = ValidDatetime(title="Created time")

	last_login = ValidDatetime(title="Last login", required=False)
	opt_out = Bool(title="Opt out flag", required=False)
	rank = Int(title="Person's rank", required=False)

class IInvitation(ITahrirModel):
	id = ValidTextLine(title=" Invitation id")
	created_on = ValidDatetime(title="Created time")
	expires_on = ValidDatetime(title="Expiration time")
	badge_id = Int(title='Badge id')
	created_by = Int(title='Person id')

class IAuthorization(ITahrirModel):
	id = Int(title="Authorization's id")
	badge_id = ValidTextLine(title=" Badge id")
	person_id = Int(title="Person id")

class IAssertion(ITahrirModel, IBadgeAssertion):
	id = ValidTextLine(title="Assertion id")
	badge_id = ValidTextLine(title="Badge id")
	person_id = Int(title="Person's id")
	salt = ValidTextLine(title="Salt")
	issued_on = ValidDatetime(title="Issue date")
	issued_for = ValidTextLine(title="Issue for", required=False)
	recipient = ValidTextLine(title="Recipient ", required=False)
	exported = Bool(title="If the assertion has been exported", default=False, 
					required=False)

class ITahrirBadgeManager(IBadgeManager):
	"""
	Interface for Tahrir database managers
	"""
	
	scoped_session = interface.Attribute('Scoped session')
		
	def update_person(person, email=None, name=None, website=None, bio=None):
		"""
		Update person information
		"""

	def update_badge(badge, description=None, criteria=None, tags=None):
		"""
		Update badge information
		"""

	def get_issuer_by_id(issuer_id):
		"""
		return the issuer by its id
		"""

	def get_person_by_id(person_id):
		"""
		return the person by its id
		"""
