#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from . import navstr
from . import openbadges
from . import tahrir_interfaces
from . import interfaces as badge_interfaces

@component.adapter(tahrir_interfaces.IPerson)
@interface.implementer(badge_interfaces.IIdentityObject)
def person_to_identity_object(person):
	result = openbadges.IdentityObject(identity=person.email,
									   type=badge_interfaces.ID_TYPE_EMAIL,
									   hashed=False,
									   salt=None)
	return result


@component.adapter(tahrir_interfaces.IBadge)
@interface.implementer(badge_interfaces.IBadgeClass)
def tahrir_badge_to_open_badge(badge):
	# Issuer HTTP URL is not set
	result = openbadges.BadgeClass(name=badge.name,
								   description=badge.description,
								   image=navstr(badge.image),
								   criteria=navstr(badge.criteria))
	return result
