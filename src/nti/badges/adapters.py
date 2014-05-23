#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from datetime import datetime

from zope import component
from zope import interface

from tahrir_api.model import Badge
from tahrir_api.model import Issuer
from tahrir_api.model import Person

from ._compact import navstr

from .openbadges.model import BadgeClass
from .openbadges.model import BadgeAssertion
from .openbadges.model import IdentityObject
from .openbadges.model import VerificationObject
from .openbadges import interfaces as open_interfaces

from .tahrir import interfaces as tahrir_interfaces

from . import interfaces
from .model import NTIPerson

@component.adapter(tahrir_interfaces.IPerson)
@interface.implementer(open_interfaces.IIdentityObject)
def tahrir_person_to_identity_object(person):
    result = IdentityObject(identity=person.email,
                            type=open_interfaces.ID_TYPE_EMAIL,
                            hashed=False,
                            salt=None)
    return result

@component.adapter(open_interfaces.IIdentityObject)
@interface.implementer(interfaces.INTIPerson)
def mozilla_identityobject_to_ntiperson(iio):
    result = NTIPerson(email=iio.identity, name=iio.identity)
    return result

@component.adapter(open_interfaces.IIdentityObject)
@interface.implementer(tahrir_interfaces.IPerson)
def mozilla_identity_object_to_tahrir_person(io):
    result = Person()
    result.email = io.identity
    return result
                                        
@component.adapter(open_interfaces.IIssuerObject)
@interface.implementer(tahrir_interfaces.IIssuer)
def mozilla_issuer_to_tahrir_issuer(issuer):
    result = Issuer()
    result.org = issuer.url
    result.image = issuer.image
    result.contact = issuer.email
    result.id = result.name = issuer.name
    return result

def tag_badge_interfaces(source, target):
    if interfaces.IEarnableBadge.providedBy(source):
        interface.alsoProvides(target, interfaces.IEarnableBadge)

    if interfaces.IEarnedBadge.providedBy(source):
        interface.alsoProvides(target, interfaces.IEarnedBadge)

@component.adapter(open_interfaces.IBadgeClass)
@interface.implementer(tahrir_interfaces.IBadge)
def mozilla_badge_to_tahrir_badge(badge):
    result = Badge()
    result.name = badge.name
    result.image = badge.image
    result.criteria = badge.criteria
    result.description = badge.description
    tag_badge_interfaces(badge, result)
    return result

@component.adapter(interfaces.INTIBadge)
@interface.implementer(open_interfaces.IBadgeClass)
def ntibadge_to_mozilla_badge(badge):
    issuer = badge.issuer
    result = BadgeClass(name=badge.name,
                        description=badge.description,
                        image=navstr(badge.image),
                        criteria=navstr(badge.criteria),
                        issuer=navstr(issuer.uri))
    tag_badge_interfaces(badge, result)
    return result

@component.adapter(interfaces.INTIAssertion)
@interface.implementer(open_interfaces.IBadgeAssertion)
def ntiassertion_to_mozilla_assertion(ast):
    badge = ast.badge
    issuer = badge.issuer
    issuedOn = ast.issuedOn
    verify = VerificationObject(type=open_interfaces.VO_TYPE_HOSTED,
                                url=navstr(issuer.org))
    result = BadgeAssertion(uid=badge.name,
                            verify=verify,
                            recipient=badge.recipient,
                            image=navstr(badge.image),
                            issuedOn=datetime.fromtimestamp(issuedOn))
    return result

@component.adapter(interfaces.INTIPerson)
@interface.implementer(tahrir_interfaces.IPerson)
def ntiperson_to_tahrir_person(nti):
    result = Person()
    result.email = nti.email
    result.nickname = nti.name
    result.bio = getattr(nti, "bio", None) or u''
    result.website = getattr(nti, "website", None) or u''
    return result
