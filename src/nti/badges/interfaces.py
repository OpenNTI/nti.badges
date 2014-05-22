#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface

from nti.utils import schema as nti_schema

class Tag(nti_schema.ValidTextLine):

	def fromUnicode(self, value):
		return super(Tag, self).fromUnicode(value.lower())

	def constraint(self, value):
		return super(Tag, self).constraint(value) and ' ' not in value

class ITaggedContent(interface.Interface):

	tags = nti_schema.TupleFromObject(title="Tags applied.",
							value_type=Tag(min_length=1, title="A single tag",
										   description=Tag.__doc__, __name__='tags'),
							unique=True,
							default=())
	
class INTIIssuer(interface.Interface):
	uri = nti_schema.Variant((
				nti_schema.TextLine(title='Issuer name'),
				nti_schema.HTTPURL(title='Issuer URL')),
				title="Issuer unique identifier")

	org = nti_schema.Variant((
				nti_schema.TextLine(title='Issuer organization'),
				nti_schema.HTTPURL(title='Issuer organization URL')),
				title="Issuer organization")

class INTIBadge(ITaggedContent):
	issuer = nti_schema.Object(INTIIssuer, title="Badge Issuer")

	name = nti_schema.TextLine(title="Badge name")

	image = nti_schema.Variant((
				nti_schema.TextLine(title='Badge image identifier'),
				nti_schema.HTTPURL(title='Badge URL')),
				title="Badge image")

	criteria = nti_schema.Variant((
					nti_schema.TextLine(title='Badge criteria identifier'),
					nti_schema.HTTPURL(title='Badge criteria URL')),
					title="Badge criteria")
	
	createdTime = nti_schema.Float(title='createdTime', required=False)

class INTIAssertion(interface.Interface):
	badge = nti_schema.Object(INTIBadge, title="Badge")
	recipient = nti_schema.Variant((
					nti_schema.TextLine(title='Badge recipient id'),
					nti_schema.HTTPURL(title='Badge recipient URL')),
					title="Badge recipient")
	issuedOn = nti_schema.Float(title="Date that the achievement was awarded")

class INTIPerson(interface.Interface):
	name = nti_schema.ValidTextLine(title="Person [unique] name")
	email = nti_schema.ValidTextLine(title="Person [unique] email")
	createdTime = nti_schema.Float(title='createdTime', required=False)
	assertions = nti_schema.ListOrTuple(nti_schema.Object(INTIAssertion, title="Assertion"),
										title="Assertions", min_length=0,
										default=(), required=False)

class IEarnableBadge(interface.Interface):
	"""
	marker interface for a earnable badbe
	"""
	pass

class IEarnedBadge(IEarnableBadge):
	"""
	marker interface for a earned badbe
	"""
	pass


class IBadgeManager(interface.Interface):
	
	def person_exists(person=None, email=None, name=None):
		"""
		check if a person exists
		"""

	def get_person(person=None, email=None, name=None):
		"""
		return a person
		"""

	def get_all_badges():
		"""
		return all available badges
		"""

	def get_person_badges(person):
		"""
		return the earned badges for the specified person
		"""

	def get_person_assertions(person):
		"""
		return the assertions for the specified person
		"""

	def delete_person(person):
		"""
		delete the user w/ the specified person
		"""
