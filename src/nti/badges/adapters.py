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

from tahrir_api.model import Badge
from tahrir_api.model import Person

from ._compact import navstr
from .openbadges import elements
from .tahrir import interfaces as tahrir_interfaces
from .openbadges import interfaces as open_interfaces

@component.adapter(tahrir_interfaces.IPerson)
@interface.implementer(open_interfaces.IIdentityObject)
def person_to_identity_object(person):
    result = elements.IdentityObject(identity=person.email,
                                       type=open_interfaces.ID_TYPE_EMAIL,
                                       hashed=False,
                                       salt=None)
    return result

@component.adapter(open_interfaces.IIdentityObject)
@interface.implementer(tahrir_interfaces.IPerson)
def identity_object_to_person(io):
    result = Person()
    result.email = io.identity
    return result

@component.adapter(tahrir_interfaces.IBadge)
@interface.implementer(open_interfaces.IBadgeClass)
def tahrir_badge_to_openbadge(badge):
    # Issuer HTTP URL is not set
    result = elements.BadgeClass(name=badge.name,
                                   description=badge.description,
                                   image=navstr(badge.image),
                                   criteria=navstr(badge.criteria))
    return result

@component.adapter(open_interfaces.IBadgeClass)
@interface.implementer(tahrir_interfaces.IBadge)
def openbadge_to_tahrir_badge(badge):
    result = Badge()
    result.name = badge.name
    result.image = badge.image
    result.criteria = badge.criteria
    result.description = badge.description
    return result
