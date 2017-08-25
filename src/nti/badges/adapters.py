#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import time
from datetime import datetime

from zope import component
from zope import interface

from tahrir_api.model import Badge
from tahrir_api.model import Issuer
from tahrir_api.model import Person

from nti.badges.interfaces import INTIBadge
from nti.badges.interfaces import INTIIssuer
from nti.badges.interfaces import INTIPerson
from nti.badges.interfaces import IEarnedBadge
from nti.badges.interfaces import INTIAssertion
from nti.badges.interfaces import IEarnableBadge

from nti.badges.model import NTIBadge
from nti.badges.model import NTIIssuer
from nti.badges.model import NTIPerson
from nti.badges.model import NTIAssertion

from nti.badges.openbadges.model import BadgeClass
from nti.badges.openbadges.model import BadgeAssertion
from nti.badges.openbadges.model import IdentityObject
from nti.badges.openbadges.model import IssuerOrganization
from nti.badges.openbadges.model import VerificationObject

from nti.badges.openbadges.interfaces import IBadgeClass
from nti.badges.openbadges.interfaces import ID_TYPE_EMAIL
from nti.badges.openbadges.interfaces import VO_TYPE_HOSTED
from nti.badges.openbadges.interfaces import IBadgeAssertion
from nti.badges.openbadges.interfaces import IIdentityObject
from nti.badges.openbadges.interfaces import IIssuerOrganization
from nti.badges.openbadges.interfaces import IVerificationObject

from nti.badges.tahrir import get_tahrir_badge_by_id
from nti.badges.tahrir import get_tahrir_issuer_by_id
from nti.badges.tahrir import get_tahrir_person_by_id

from nti.badges.tahrir.interfaces import IBadge as ITahrirBadge
from nti.badges.tahrir.interfaces import IIssuer as ITahrirIssuer
from nti.badges.tahrir.interfaces import IPerson as ITahrirPerson
from nti.badges.tahrir.interfaces import IAssertion as ITahrirAssertion


def tag_badge_interfaces(source, target):
    if IEarnableBadge.providedBy(source):
        interface.alsoProvides(target, IEarnableBadge)

    if IEarnedBadge.providedBy(source):
        interface.alsoProvides(target, IEarnedBadge)


@interface.implementer(IIdentityObject)
def basestring_to_mozilla_indentity_object(source):
    result = IdentityObject(identity=source,
                            type=ID_TYPE_EMAIL,
                            hashed=False,
                            salt=None)
    return result


@interface.implementer(ITahrirPerson)
def basestring_to_tahrir_person(source):
    result = Person()
    result.email = source
    result.nickname = source
    result.website = result.bio = u''
    result.created_on = datetime.now()
    return result


@interface.implementer(INTIPerson)
def basestring_to_ntiperson(source):
    result = NTIPerson(name=source,
                       email=source,
                       createdTime=time.time())
    return result


@interface.implementer(ITahrirBadge)
def basestring_to_tahrir_badge(source):
    result = Badge()
    result.name = source
    return result


@interface.implementer(ITahrirIssuer)
def basestring_to_tahrir_issuer(source):
    result = Issuer()
    result.name = source
    return result


@interface.implementer(ITahrirIssuer)
def collection_to_tahrir_issuer(lst):
    result = Issuer()
    result.name = lst[0]
    result.origin = lst[1] if len(lst) > 1 else None
    return result

# tahrir->


@component.adapter(ITahrirIssuer)
@interface.implementer(IVerificationObject)
def tahrir_issuer_to_mozilla_verification_object(issuer):
    verify = VerificationObject(type=VO_TYPE_HOSTED,
                                url=issuer.origin)
    return verify


@component.adapter(ITahrirPerson)
@interface.implementer(IIdentityObject)
def tahrir_person_to_mozilla_identity_object(person):
    result = IdentityObject(identity=person.email,
                            type=ID_TYPE_EMAIL,
                            hashed=False,
                            salt=None)
    return result


@component.adapter(ITahrirIssuer)
@interface.implementer(IIssuerOrganization)
def tahrir_issuer_to_mozilla_issuer(issuer):
    result = IssuerOrganization(name=issuer.name,
                                url=issuer.origin,
                                email=issuer.contact,
                                description=issuer.org)
    return result


@component.adapter(ITahrirBadge)
@interface.implementer(IBadgeClass)
def tahrir_badge_to_mozilla_badge(badge):
    tags = badge.tags or ''
    tags = tuple(x.lower() for x in tags.split(',') if x)
    # request from the db if possible.
    # We've seen some some NoSuchColumnError in MySQL when
    # trying to use the badge issuer reference
    issuer_id = badge.issuer_id
    issuer = get_tahrir_issuer_by_id(issuer_id) if issuer_id is not None else None
    issuer = badge.issuer if issuer is None else issuer
    issuer = IIssuerOrganization(issuer, None)

    result = BadgeClass(tags=tags,
                        name=badge.name,
                        image=badge.image,
                        criteria=badge.criteria,
                        description=badge.description)
    if issuer:
        result.issuer = issuer
    else:
        logger.warn("Could not set issuer for badge %s", result.name)
    tag_badge_interfaces(badge, result)
    return result


@component.adapter(ITahrirAssertion)
@interface.implementer(IBadgeAssertion)
def tahrir_assertion_to_mozilla_assertion(assertion):
    badge_id = assertion.badge_id
    badge = get_tahrir_badge_by_id(badge_id) if badge_id is not None else None
    badge = assertion.badge if badge is None else badge

    person_id = assertion.person_id
    person = get_tahrir_person_by_id(person_id) if person_id is not None else None
    person = assertion.person if person is None else person

    # issuer
    issuer_id = badge.issuer_id
    issuer = get_tahrir_issuer_by_id(
        issuer_id) if issuer_id is not None else None
    issuer = badge.issuer if issuer is None else issuer
    verify = IVerificationObject(issuer)

    # recipient
    salt = getattr(assertion, 'salt', None)
    identity = assertion.recipient if salt else person.email
    recipient = IdentityObject(salt=salt,
                               identity=identity,
                               type=ID_TYPE_EMAIL,
                               hashed=(True if salt else False),)

    # exported
    exported = getattr(assertion, 'exported', None) or False

    # assertion
    aid = assertion.id or u"%s -> %s" % (badge.name, person.email)
    result = BadgeAssertion(uid=aid,
                            verify=verify,
                            image=badge.image,
                            recipient=recipient,
                            issuedOn=assertion.issued_on,
                            badge=IBadgeClass(badge),
                            exported=exported)
    return result


@component.adapter(ITahrirAssertion)
@interface.implementer(IBadgeClass)
def tahrir_assertion_to_mozilla_badge(assertion):
    return IBadgeClass(assertion.badge)


@component.adapter(ITahrirIssuer)
@interface.implementer(INTIIssuer)
def tahrir_issuer_to_ntiissuer(issuer):
    result = NTIIssuer(name=issuer.name,
                       origin=issuer.origin,
                       email=issuer.contact,
                       organization=issuer.org,
                       createdTime=time.mktime(issuer.created_on.timetuple()))
    return result


@component.adapter(ITahrirBadge)
@interface.implementer(INTIBadge)
def tahrir_badge_to_ntibadge(badge):
    tags = badge.tags or u''
    tags = tuple(x.lower() for x in tags.split(',') if x)
    issuer = INTIIssuer(badge.issuer, None)
    result = NTIBadge(issuer=issuer,
                      tags=tuple(tags),
                      name=badge.name,
                      image=badge.image,
                      criteria=badge.criteria,
                      description=badge.description,
                      createdTime=time.mktime(badge.created_on.timetuple()))
    return result


@component.adapter(ITahrirAssertion)
@interface.implementer(INTIAssertion)
def tahrir_assertion_to_ntiassertion(assertion):
    badge = INTIBadge(assertion.badge)
    interface.alsoProvides(badge, IEarnedBadge)
    exported = getattr(assertion, 'exported', None) or False
    issuedOn = time.mktime(assertion.issued_on.timetuple())
    result = NTIAssertion(badge=badge,
                          issuedOn=issuedOn,
                          uid=assertion.id,
                          recipient=assertion.recipient,
                          person=INTIPerson(assertion.person),
                          salt=getattr(assertion, 'salt', None),
                          exported=exported)
    return result


@component.adapter(ITahrirPerson)
@interface.implementer(INTIPerson)
def tahrir_person_to_ntiperson(person):
    result = NTIPerson(email=person.email,
                       name=person.nickname,
                       createdTime=time.mktime(person.created_on.timetuple()))
    # not part of the interface but keep them
    result.bio = person.bio
    result.website = person.website
    return result

# nti->


@component.adapter(INTIIssuer)
@interface.implementer(ITahrirIssuer)
def ntiissuer_to_tahrir_issuer(issuer):
    result = Issuer()
    result.name = issuer.name
    result.contact = issuer.email
    result.origin = issuer.origin
    result.org = issuer.organization
    return result


@component.adapter(INTIBadge)
@interface.implementer(ITahrirBadge)
def ntibadge_to_tahrir_badge(badge):
    # XXX: Issuer is not set
    tags = ','.join(badge.tags)
    result = Badge(tags=tags,
                   name=badge.name,
                   image=badge.image,
                   criteria=badge.criteria,
                   description=badge.description,
                   created_on=datetime.fromtimestamp(badge.createdTime))
    tag_badge_interfaces(badge, result)
    return result


@component.adapter(INTIIssuer)
@interface.implementer(IVerificationObject)
def ntiissuer_to_mozilla_verification_object(issuer):
    verify = VerificationObject(url=issuer.origin,
                                type=VO_TYPE_HOSTED)
    return verify


@component.adapter(INTIIssuer)
@interface.implementer(IIssuerOrganization)
def ntiissuer_to_mozilla_issuer(issuer):
    result = IssuerOrganization(name=issuer.name,
                                url=issuer.origin,
                                email=issuer.email)
    return result


@component.adapter(INTIBadge)
@interface.implementer(IBadgeClass)
def ntibadge_to_mozilla_badge(badge):
    issuer = badge.issuer
    result = BadgeClass(tags=badge.tags,
                        name=badge.name,
                        image=badge.image,
                        issuer=issuer.origin,
                        criteria=badge.criteria,
                        description=badge.description)
    tag_badge_interfaces(badge, result)
    return result


@component.adapter(INTIAssertion)
@interface.implementer(IBadgeAssertion)
def ntiassertion_to_mozilla_assertion(assertion):
    badge = assertion.badge
    issuer = badge.issuer
    issuedOn = assertion.issuedOn
    identity = assertion.recipient or assertion.person
    verify = IVerificationObject(issuer)
    recipient = IdentityObject(identity=identity,
                               type=ID_TYPE_EMAIL,
                               salt=assertion.salt,
                               hashed=(assertion.salt is not None))
    result = BadgeAssertion(verify=verify,
                            uid=assertion.id,
                            image=badge.image,
                            recipient=recipient,
                            badge=IBadgeClass(badge),
                            exported=assertion.exported,
                            issuedOn=datetime.fromtimestamp(issuedOn))
    return result


@component.adapter(INTIAssertion)
@interface.implementer(IBadgeClass)
def ntiassertion_to_mozilla_badge(assertion):
    result = IBadgeClass(assertion.badge)
    return result


@component.adapter(INTIPerson)
@interface.implementer(ITahrirPerson)
def ntiperson_to_tahrir_person(nti):
    result = Person()
    result.email = nti.email
    result.nickname = nti.name
    result.bio = getattr(nti, "bio", None) or u''
    result.website = getattr(nti, "website", None) or u''
    result.created_on = datetime.fromtimestamp(nti.createdTime)
    return result

# mozilla->


@component.adapter(IIdentityObject)
@interface.implementer(ITahrirPerson)
def mozilla_identity_object_to_tahrir_person(io):
    result = Person()
    result.email = io.identity
    return result


@component.adapter(IIssuerOrganization)
@interface.implementer(ITahrirIssuer)
def mozilla_issuer_to_tahrir_issuer(issuer):
    result = Issuer()
    result.org = issuer.url
    result.name = issuer.name
    result.origin = issuer.url
    result.image = issuer.image
    result.contact = issuer.email
    return result


@component.adapter(IIssuerOrganization)
@interface.implementer(INTIIssuer)
def mozilla_issuer_to_ntiisuer(issuer):
    result = NTIIssuer(name=issuer.name,
                       origin=issuer.url,
                       email=issuer.email,
                       organization=issuer.url)
    return result


@component.adapter(IIdentityObject)
@interface.implementer(INTIPerson)
def mozilla_identityobject_to_ntiperson(iio):
    result = NTIPerson(name=iio.identity,
                       email=iio.identity)
    return result


@component.adapter(IBadgeClass)
@interface.implementer(ITahrirBadge)
def mozilla_badge_to_tahrir_badge(badge):
    # XXX: Issuer is not set
    result = Badge()
    result.name = badge.name
    result.image = badge.image
    result.criteria = badge.criteria
    result.description = badge.description
    result.tags = ','.join(badge.tags or ())
    tag_badge_interfaces(badge, result)
    return result


@component.adapter(IBadgeClass)
@interface.implementer(INTIBadge)
def mozilla_badge_to_ntibadge(badge):
    # XXX: Issuer is not set
    result = NTIBadge(tags=badge.tags,
                      name=badge.name,
                      image=badge.image,
                      criteria=badge.criteria,
                      description=badge.description,
                      createdTime=time.time())
    return result
