#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import time
from datetime import datetime

from zope import component
from zope import interface

from tahrir_api.model import Badge
from tahrir_api.model import Issuer
from tahrir_api.model import Person

from .openbadges.model import BadgeClass
from .openbadges.model import BadgeAssertion
from .openbadges.model import IdentityObject
from .openbadges.model import IssuerOrganization
from .openbadges.model import VerificationObject

from .openbadges.interfaces import IBadgeClass
from .openbadges.interfaces import ID_TYPE_EMAIL
from .openbadges.interfaces import VO_TYPE_HOSTED
from .openbadges.interfaces import IBadgeAssertion
from .openbadges.interfaces import IIdentityObject
from .openbadges.interfaces import IIssuerOrganization
from .openbadges.interfaces import IVerificationObject

from .tahrir import get_tahrir_badge_by_id
from .tahrir import get_tahrir_issuer_by_id
from .tahrir import get_tahrir_person_by_id
from .tahrir.interfaces import IBadge as ITahrirBadge
from .tahrir.interfaces import IIssuer as ITahrirIssuer
from .tahrir.interfaces import IPerson as ITahrirPerson
from .tahrir.interfaces import IAssertion as ITahrirAssertion

from .utils import safestr

from .model import NTIBadge
from .model import NTIIssuer
from .model import NTIPerson
from .model import NTIAssertion

from .interfaces import INTIBadge
from .interfaces import INTIIssuer
from .interfaces import INTIPerson
from .interfaces import IEarnedBadge
from .interfaces import INTIAssertion
from .interfaces import IEarnableBadge

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
	result.website = result.bio = ''
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
								url=safestr(issuer.origin))
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
	result = IssuerOrganization(url=safestr(issuer.origin),
								name=safestr(issuer.name),
								email=safestr(issuer.contact),
								description=safestr(issuer.org))
	return result

@component.adapter(ITahrirBadge)
@interface.implementer(IBadgeClass)
def tahrir_badge_to_mozilla_badge(badge):
	tags = tuple(safestr(x.lower()) for x in ((badge.tags or '').split(',')) if x)
	## request from the db if possible.
	## We've seen some some NoSuchColumnError in MySQL when
	## trying to use the badge issuer reference
	issuer_id = badge.issuer_id
	issuer = get_tahrir_issuer_by_id(issuer_id) if issuer_id is not None else badge.issuer
	issuer = IIssuerOrganization(issuer, None)
	
	result = BadgeClass(tags=tags,
						name=safestr(badge.name),
						image=safestr(badge.image),
						criteria=safestr(badge.criteria),
						description=safestr(badge.description))
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
	badge = get_tahrir_badge_by_id(badge_id) if badge_id is not None else assertion.badge
	
	person_id = assertion.person_id
	person = get_tahrir_person_by_id(badge_id) if person_id is not None else assertion.person

	# issuer
	issuer_id = badge.issuer_id
	issuer = get_tahrir_issuer_by_id(issuer_id) if issuer_id is not None else badge.issuer
	verify = IVerificationObject(issuer)

	# recipient
	salt = getattr(assertion, 'salt', None)
	identity = assertion.recipient if salt else person.email
	recipient = IdentityObject(salt=salt,
							   identity=identity,
							   hashed=(True if salt else False),
							   type=ID_TYPE_EMAIL)

	# exported
	exported = getattr(assertion, 'exported', None) or False
	
	# assertion
	aid = assertion.id or u"%s -> %s" % (badge.name, person.email)
	result = BadgeAssertion(uid=aid,
							verify=verify,
							recipient=recipient,
							image=safestr(badge.image),
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
	result = NTIIssuer(name=safestr(issuer.name),
					   origin=safestr(issuer.origin),
					   email=safestr(issuer.contact),
					   organization=safestr(issuer.org),
					   createdTime=time.mktime(issuer.created_on.timetuple()))
	return result

@component.adapter(ITahrirBadge)
@interface.implementer(INTIBadge)
def tahrir_badge_to_ntibadge(badge):
	tags = tuple(safestr(x.lower()) for x in ((badge.tags or '').split(',')) if x)
	issuer = INTIIssuer(badge.issuer, None)
	result = NTIBadge(issuer=issuer,
					  tags=tuple(tags),
					  name=safestr(badge.name),
					  image=safestr(badge.image),
					  criteria=safestr(badge.criteria),
					  description=safestr(badge.description),
					  createdTime=time.mktime(badge.created_on.timetuple()))
	return result

@component.adapter(ITahrirAssertion)
@interface.implementer(INTIAssertion)
def tahrir_assertion_to_ntiassertion(assertion):
	badge = INTIBadge(assertion.badge)
	interface.alsoProvides(badge, IEarnedBadge)
	exported = getattr(assertion, 'exported', None) or False
	issuedOn = time.mktime(assertion.issued_on.timetuple())
	result = NTIAssertion(uid=assertion.id,
						  badge=badge,
						  issuedOn=issuedOn,
						  person=INTIPerson(assertion.person),
						  recipient=safestr(assertion.recipient),
						  salt=getattr(assertion, 'salt', None),
						  exported=exported)
	return result

@component.adapter(ITahrirPerson)
@interface.implementer(INTIPerson)
def tahrir_person_to_ntiperson(person):
	result = NTIPerson(name=safestr(person.nickname),
					   email=safestr(person.email),
					   createdTime=time.mktime(person.created_on.timetuple()))
	# not part of the interface but keep them
	result.bio = safestr(person.bio)
	result.website = safestr(person.website)
	return result

# nti->

@component.adapter(INTIIssuer)
@interface.implementer(ITahrirIssuer)
def ntiissuer_to_tahrir_issuer(issuer):
	result = Issuer()
	result.name = safestr(issuer.name)
	result.contact = safestr(issuer.email)
	result.origin = safestr(issuer.origin)
	result.org = safestr(issuer.organization)
	return result

@component.adapter(INTIBadge)
@interface.implementer(ITahrirBadge)
def ntibadge_to_tahrir_badge(badge):
	# XXX: Issuer is not set
	tags = ','.join(badge.tags)
	result = Badge(tags=tags,
				   name=safestr(badge.name),
				   image=safestr(badge.image),
				   criteria=safestr(badge.criteria),
				   description=safestr(badge.description),
				   created_on=datetime.fromtimestamp(badge.createdTime))
	tag_badge_interfaces(badge, result)
	return result

@component.adapter(INTIIssuer)
@interface.implementer(IVerificationObject)
def ntiissuer_to_mozilla_verification_object(issuer):
	verify = VerificationObject(type=VO_TYPE_HOSTED,
								url=safestr(issuer.origin))
	return verify

@component.adapter(INTIIssuer)
@interface.implementer(IIssuerOrganization)
def ntiissuer_to_mozilla_issuer(issuer):
	result = IssuerOrganization(name=safestr(issuer.name),
						  		url=safestr(issuer.origin),
						  		email=issuer.email)
	return result

@component.adapter(INTIBadge)
@interface.implementer(IBadgeClass)
def ntibadge_to_mozilla_badge(badge):
	issuer = badge.issuer
	result = BadgeClass(tags=badge.tags,
						name=safestr(badge.name),
						image=safestr(badge.image),
						issuer=safestr(issuer.origin),
						description=badge.description,
						criteria=safestr(badge.criteria))
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
							   hashed=(assertion.salt is not None),
							   salt=assertion.salt)
	result = BadgeAssertion(uid=assertion.id,
							verify=verify,
							recipient=recipient,
							image=safestr(badge.image),
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
	result.email = safestr(nti.email)
	result.nickname = safestr(nti.name)
	result.bio = safestr(getattr(nti, "bio", None) or '')
	result.website = safestr(getattr(nti, "website", None) or '')
	result.created_on = datetime.fromtimestamp(nti.createdTime)
	return result

# mozilla->

@component.adapter(IIdentityObject)
@interface.implementer(ITahrirPerson)
def mozilla_identity_object_to_tahrir_person(io):
	result = Person()
	result.email = safestr(io.identity)
	return result

@component.adapter(IIssuerOrganization)
@interface.implementer(ITahrirIssuer)
def mozilla_issuer_to_tahrir_issuer(issuer):
	result = Issuer()
	result.org = safestr(issuer.url)
	result.name = safestr(issuer.name)
	result.origin = safestr(issuer.url)
	result.image = safestr(issuer.image)
	result.contact = safestr(issuer.email)
	return result

@component.adapter(IIssuerOrganization)
@interface.implementer(INTIIssuer)
def mozilla_issuer_to_ntiisuer(issuer):
	result = NTIIssuer(name=safestr(issuer.name),
					   origin=safestr(issuer.url),
					   email=safestr(issuer.email),
					   organization=safestr(issuer.url))
	return result

@component.adapter(IIdentityObject)
@interface.implementer(INTIPerson)
def mozilla_identityobject_to_ntiperson(iio):
	result = NTIPerson(email=safestr(iio.identity), name=safestr(iio.identity))
	return result

@component.adapter(IBadgeClass)
@interface.implementer(ITahrirBadge)
def mozilla_badge_to_tahrir_badge(badge):
	# XXX: Issuer is not set
	result = Badge()
	result.name = safestr(badge.name)
	result.image = safestr(badge.image)
	result.criteria = safestr(badge.criteria)
	result.tags = safestr(','.join(badge.tags))
	result.description = safestr(badge.description)
	tag_badge_interfaces(badge, result)
	return result

@component.adapter(IBadgeClass)
@interface.implementer(INTIBadge)
def mozilla_badge_to_ntibadge(badge):
	# XXX: Issuer is not set
	result = NTIBadge(tags=badge.tags,
					  name=safestr(badge.name),
					  image=safestr(badge.image),
					  criteria=safestr(badge.criteria),
					  description=safestr(badge.description),
					  createdTime=time.time())
	return result
