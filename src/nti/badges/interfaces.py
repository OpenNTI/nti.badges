#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface

from nti.utils import schema as nti_schema

class INTIIssuer(interface.Interface):
	"""
	marker interface for a badge issuer
	"""
	uri = nti_schema.Variant((
				nti_schema.TextLine(title='Issuer name'),
				nti_schema.HTTPURL(title='Issuer URL')),
				title="Issuer unique identifier")

	org = nti_schema.Variant((
				nti_schema.TextLine(title='Issuer organization'),
				nti_schema.HTTPURL(title='Issuer organization URL')),
				title="Issuer organization")

class INTIBadge(interface.Interface):
	"""
	marker interface for a badge
	"""
	issuer = nti_schema.Object(INTIIssuer, title="issuer url")
	data = nti_schema.Object(interface.Interface, title="badge data")

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

class INTIAssertion(interface.Interface):
	"""
	marker interface for a badge
	"""
	badge = nti_schema.Object(INTIBadge, title="badge")
	recipient = nti_schema.Variant((
					nti_schema.TextLine(title='Badge recipient id'),
					nti_schema.HTTPURL(title='Badge recipient URL')),
					title="Badge recipient")
	issuedOn = nti_schema.ValidDatetime(title="Date that the achievement was awarded")

class IBadgeManager(interface.Interface):
	
	def get_all_badges():
		"""
		return all availble badges
		"""

	def get_user_badges(userid):
		"""
		return the earned badges for the specified user
		"""

	def get_user_assertions(userid):
		"""
		return the assertions for the specified user
		"""

	def delete_user(userid):
		"""
		delete the user w/ the specified userid
		"""
