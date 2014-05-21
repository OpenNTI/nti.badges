#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface

class INTIIssuer(interface.Interface):
	"""
	marker interface for a badge issuer
	"""
	url = interface.Attribute("issuer url")

class INTIBadge(interface.Interface):
	"""
	marker interface for a badge
	"""
	issuer = interface.Attribute("issuer url")
	data = interface.Attribute("badge data")

class INTIAssertion(interface.Interface):
	"""
	marker interface for a badge
	"""
	badge = interface.Attribute("badge")
	issuer = interface.Attribute("issuer url")
	recipient = interface.Attribute("recipient id")
	issuedOn = interface.Attribute("created/issue date")

class IBadgeManager(interface.Interface):
	
	def get_all_badges():
		"""
		return all availble badges
		"""

	def get_user_assertions(userid):
		"""
		return the assertions for the specified user
		"""

	def delete_user(userid):
		"""
		delete the user w/ the specified userid
		"""
