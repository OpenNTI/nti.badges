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

from .openbadges.elements import BadgeClass
from .openbadges.elements import BadgeAssertion
from .openbadges.elements import IdentityObject
from .openbadges.elements import VerificationObject
from .openbadges import interfaces as open_interfaces

from .tahrir import interfaces as tahrir_interfaces

@component.adapter(tahrir_interfaces.IPerson)
@interface.implementer(open_interfaces.IIdentityObject)
def person_to_identity_object(person):
    result = IdentityObject(identity=person.email,
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

@component.adapter(open_interfaces.IBadgeClass)
@interface.implementer(tahrir_interfaces.IBadge)
def open_badge_to_tahrir_badge(badge):
    result = Badge()
    result.name = badge.name
    result.image = badge.image
    result.criteria = badge.criteria
    result.description = badge.description
    return result

@component.adapter(tahrir_interfaces.ITahrirBadge)
@interface.implementer(open_interfaces.IBadgeClass)
def tahrir_badge_to_open_badge(badge):
    issuer = badge.issuer
    data = badge.data
    result = BadgeClass(name=data.name,
                        description=data.description,
                        image=navstr(data.image),
                        criteria=navstr(data.criteria),
                        issuer=navstr(issuer.uri))
    return result

@component.adapter(tahrir_interfaces.ITahrirAssertion)
@interface.implementer(open_interfaces.IBadgeAssertion)
def tahrir_assertion_to_open_assertion(ast):
    badge, issuedOn = ast.badge, ast.issuedOn
    issuer = badge.issuer
    verify = VerificationObject(type=open_interfaces.VO_TYPE_HOSTED,
                                url=navstr(issuer.org))
    result = BadgeAssertion(uid=badge.name,
                            recipient=badge.recipient,
                            verify=verify,
                            issuedOn=issuedOn,
                            image=navstr(badge.image),)
    return result
