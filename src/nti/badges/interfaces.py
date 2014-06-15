#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface

# XXX: Note: These will move, pending a better separation
# of the base utility packages.
from nti.contentfragments.schema import PlainTextLine

# XXX: Note: These will move, pending a better separation
# of the base utility packages.
from nti.utils.schema import Number
from nti.utils.schema import Object
from nti.utils.schema import Variant
from nti.utils.schema import ValidText
from nti.utils.schema import TupleFromObject
from nti.utils.schema import DecodingValidTextLine as ValidTextLine
TextLine = ValidTextLine

# XXX: Note: These are temporary, pending a better
# separation of the base content model. This package
# in general should avoid dependencies on `nti.dataserver`
from nti.dataserver.interfaces import ICreatedTime

class Tag(PlainTextLine):
	"""
	Requires its content to be only one plain text word that is lowercased.
	"""

	def fromUnicode(self, value):
		return super(Tag, self).fromUnicode(value.lower())

	def constraint(self, value):
		return super(Tag, self).constraint(value)

class ITaggedContent(interface.Interface):
	"""
	Something that can contain tags.
	"""

	tags = TupleFromObject(title="Tags applied by the user.",
						   value_type=Tag(min_length=1, title="A single tag",
										  description=Tag.__doc__, __name__='tags'),
						   unique=True,
						   default=())

class IBadgeIssuer(interface.Interface):
	"""
	marker interface for all badge issuers
	"""

class IBadgeAssertion(interface.Interface):
	"""
	marker interface for all badge assertion
	"""
	uid = ValidTextLine(title="The unique id of the assertion")

class IBadgeClass(interface.Interface):
	"""
	marker interface for all badges
	"""
	name = ValidTextLine(title="The name of the badge")

class INTIIssuer(IBadgeIssuer,
				 ICreatedTime):
	name = ValidTextLine(title='Issuer name')

	origin = ValidTextLine(title='Issuer origin')

	organization = TextLine(title='Issuer organization')

	email = ValidTextLine(title="Issuer email")

class INTIBadge(ITaggedContent,
				IBadgeClass,
				ICreatedTime):
	issuer = Object(INTIIssuer,
					title="Badge Issuer",
					required=False)

	name = ValidTextLine(title="Badge name")

	description = ValidText(title="Badge description",
							required=False,
							default='')

	image = ValidTextLine(title='Badge image identifier/URL')

	criteria = TextLine(title='Badge criteria identifier/URL')

class INTIPerson(ICreatedTime):
	name = ValidTextLine(title="Person [unique] name")
	email = ValidTextLine(title="Person [unique] email")

class INTIAssertion(IBadgeAssertion):
	uid = ValidTextLine(title="Assertion id")
	badge = Object(INTIBadge, title="Badge")
	person = Variant((
				ValidTextLine(title="Badge recipient name/email"),
				Object(INTIPerson, title="Badge recipient person")),
				title="Badge recipient")
	issuedOn = Number(title="Date that the achievement was awarded",
					  default=0)
	recipient = ValidTextLine(title="Badge recipient hash", required=False)
	salt = ValidTextLine(title="One-way function to hash person", required=False)

class IEarnableBadge(interface.Interface):
	"""
	marker interface for a earnable badbe
	"""

class IEarnedBadge(IEarnableBadge):
	"""
	marker interface for a earned badbe
	"""

class IBadgeManager(interface.Interface):

	def person_exists(person=None, name=None):
		"""
		check if a person exists
		"""

	def get_person(person=None, email=None, name=None):
		"""
		return a person
		"""

	def badge_exists(badge):
		"""
		check if the specifed badge exists
		"""

	def add_badge(badge, issuer=None):
		"""
		add the specifed badge
		"""

	def update_badge(badge, description=None, criteria=None):
		"""
		update the information regarding a batch
		"""
		
	def get_badge(badge):
		"""
		return the specifed badge
		"""

	def get_all_badges():
		"""
		return all available badges
		"""

	def get_person_badges(person):
		"""
		return the earned badges for the specified person
		"""

	def get_assertion_by_id(assertion_id):
		"""
		return the badge assertion for the specified id
		"""
		
	def get_assertion(person, badge):
		"""
		return a badge assertion for the specified person
		"""

	def add_assertion(person, badge):
		"""
		add a badge assertion for the specified person
		"""

	def remove_assertion(person, badge):
		"""
		remove a badge assertion from the specified person
		"""

	def assertion_exists(person, badge):
		"""
		check if a badge assertion exists
		"""

	def get_person_assertions(person):
		"""
		return the assertions for the specified person
		"""

	def delete_person(person):
		"""
		delete the user w/ the specified person
		"""

	def issuer_exists(issuer, origin=None):
		"""
		return the specified issuer exists
		"""

	def get_issuer(issuer, origin=None):
		"""
		return the specified issuer
		"""

	def add_issuer(issuer):
		"""
		add the specified :class:`.IIssuer` object.
		"""
