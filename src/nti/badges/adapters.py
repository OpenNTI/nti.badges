#!/usr/bin/env python
# -*- coding: utf-8 -*
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
from .openbadges import interfaces as open_interfaces

from .tahrir import interfaces as tahrir_interfaces

from .utils import safestr
from .model import NTIBadge
from .model import NTIIssuer
from .model import NTIPerson
from .model import NTIAssertion

from . import interfaces
from . import get_tahrir_badge_by_id
from . import get_tahrir_person_by_id
from . import get_tahrir_issuer_by_id

def tag_badge_interfaces(source, target):
	if interfaces.IEarnableBadge.providedBy(source):
		interface.alsoProvides(target, interfaces.IEarnableBadge)

	if interfaces.IEarnedBadge.providedBy(source):
		interface.alsoProvides(target, interfaces.IEarnedBadge)

@interface.implementer(open_interfaces.IIdentityObject)
def basestring_to_mozilla_indentity_object(source):
	result = IdentityObject(identity=source,
							type=open_interfaces.ID_TYPE_EMAIL,
							hashed=False,
							salt=None)
	return result

@interface.implementer(tahrir_interfaces.IPerson)
def basestring_to_tahrir_person(source):
	result = Person()
	result.email = source
	result.nickname = source
	result.website = result.bio = ''
	result.created_on = datetime.now()
	return result

@interface.implementer(interfaces.INTIPerson)
def basestring_to_ntiperson(source):
	result = NTIPerson(name=source,
					   email=source,
					   createdTime=time.time())
	return result

@interface.implementer(tahrir_interfaces.IBadge)
def basestring_to_tahrir_badge(source):
	result = Badge()
	result.name = source
	return result

@interface.implementer(tahrir_interfaces.IIssuer)
def basestring_to_tahrir_issuer(source):
	result = Issuer()
	result.name = source
	return result

@interface.implementer(tahrir_interfaces.IIssuer)
def collection_to_tahrir_issuer(lst):
	result = Issuer()
	result.name = lst[0]
	result.origin = lst[1] if len(lst) > 1 else None
	return result

# tahrir->

@component.adapter(tahrir_interfaces.IIssuer)
@interface.implementer(open_interfaces.IVerificationObject)
def tahrir_issuer_to_mozilla_verification_object(issuer):
	verify = VerificationObject(type=open_interfaces.VO_TYPE_HOSTED,
								url=safestr(issuer.origin))
	return verify

@component.adapter(tahrir_interfaces.IPerson)
@interface.implementer(open_interfaces.IIdentityObject)
def tahrir_person_to_mozilla_identity_object(person):
	result = IdentityObject(identity=person.email,
							type=open_interfaces.ID_TYPE_EMAIL,
							hashed=False,
							salt=None)
	return result

@component.adapter(tahrir_interfaces.IIssuer)
@interface.implementer(open_interfaces.IIssuerOrganization)
def tahrir_issuer_to_mozilla_issuer(issuer):
	result = IssuerOrganization(url=safestr(issuer.origin),
								name=safestr(issuer.name),
								email=safestr(issuer.contact),
								description=safestr(issuer.org))
	return result

@component.adapter(tahrir_interfaces.IBadge)
@interface.implementer(open_interfaces.IBadgeClass)
def tahrir_badge_to_mozilla_badge(badge):
	tags = tuple(safestr(x.lower()) for x in ((badge.tags or '').split(',')) if x)
	# request from the db if possible. We've seen some some NoSuchColumnError in MySQL when
	# trying to use the badge issuer reference
	issuer_id = badge.issuer_id
	issuer = get_tahrir_issuer_by_id(issuer_id) if issuer_id is not None else badge.issuer
	issuer_origin = issuer.origin if issuer is not None else None
	# we have an issuer origin. Should return the whole issuer?
	result = BadgeClass(tags=tags,
						name=safestr(badge.name),
						image=safestr(badge.image),
						criteria=safestr(badge.criteria),
						description=safestr(badge.description))
	if issuer_origin:
		result.issuer = safestr(issuer_origin)
	else:
		logger.warn("Could not set issuer for badge %s", result.name)
	tag_badge_interfaces(badge, result)
	return result

@component.adapter(tahrir_interfaces.IAssertion)
@interface.implementer(open_interfaces.IBadgeAssertion)
def tahrir_assertion_to_mozilla_assertion(assertion):
	badge_id = assertion.badge_id
	badge = get_tahrir_badge_by_id(badge_id) if badge_id is not None else assertion.badge
	
	person_id = assertion.person_id
	person = get_tahrir_person_by_id(badge_id) if person_id is not None else assertion.person

	# issuer
	issuer_id = badge.issuer_id
	issuer = get_tahrir_issuer_by_id(issuer_id) if issuer_id is not None else badge.issuer
	verify = open_interfaces.IVerificationObject(issuer)

	# recipient
	salt = getattr(assertion, 'salt', None)
	identity = assertion.recipient if salt else person.email
	recipient = IdentityObject(salt=salt,
							   identity=identity,
							   hashed=(True if salt else False),
							   type=open_interfaces.ID_TYPE_EMAIL)

	# assertion
	aid = assertion.id or u"%s -> %s" % (badge.name, person.email)
	result = BadgeAssertion(uid=aid,
							verify=verify,
							recipient=recipient,
							image=safestr(badge.image),
							issuedOn=assertion.issued_on,
							badge=open_interfaces.IBadgeClass(badge))
	return result

@component.adapter(tahrir_interfaces.IIssuer)
@interface.implementer(interfaces.INTIIssuer)
def tahrir_issuer_to_ntiissuer(issuer):
	result = NTIIssuer(name=safestr(issuer.name),
					   origin=safestr(issuer.origin),
					   email=safestr(issuer.contact),
					   organization=safestr(issuer.org),
					   createdTime=time.mktime(issuer.created_on.timetuple()))
	return result

@component.adapter(tahrir_interfaces.IBadge)
@interface.implementer(interfaces.INTIBadge)
def tahrir_badge_to_ntibadge(badge):
	tags = tuple(safestr(x.lower()) for x in ((badge.tags or '').split(',')) if x)
	issuer = interfaces.INTIIssuer(badge.issuer, None)
	result = NTIBadge(issuer=issuer,
					  tags=tuple(tags),
					  name=safestr(badge.name),
					  image=safestr(badge.image),
					  criteria=safestr(badge.criteria),
					  description=safestr(badge.description),
					  createdTime=time.mktime(badge.created_on.timetuple()))
	return result

@component.adapter(tahrir_interfaces.IAssertion)
@interface.implementer(interfaces.INTIAssertion)
def tahrir_assertion_to_ntiassertion(ast):
	badge = interfaces.INTIBadge(ast.badge)
	interface.alsoProvides(badge, interfaces.IEarnedBadge)
	issuedOn = time.mktime(ast.issued_on.timetuple())
	result = NTIAssertion(uid=ast.id,
						  badge=badge,
						  issuedOn=issuedOn,
						  person=interfaces.INTIPerson(ast.person),
						  recipient=safestr(ast.recipient),
						  salt=getattr(ast, 'salt', None))
	return result

@component.adapter(tahrir_interfaces.IPerson)
@interface.implementer(interfaces.INTIPerson)
def tahrir_person_to_ntiperson(person):
	result = NTIPerson(name=safestr(person.nickname),
					   email=safestr(person.email),
					   createdTime=time.mktime(person.created_on.timetuple()))
	# not part of the interface but keep them
	result.bio = safestr(person.bio)
	result.website = safestr(person.website)
	return result

# nti->

@component.adapter(interfaces.INTIIssuer)
@interface.implementer(tahrir_interfaces.IIssuer)
def ntiissuer_to_tahrir_issuer(issuer):
	result = Issuer()
	result.name = safestr(issuer.name)
	result.contact = safestr(issuer.email)
	result.origin = safestr(issuer.origin)
	result.org = safestr(issuer.organization)
	return result

@component.adapter(interfaces.INTIBadge)
@interface.implementer(tahrir_interfaces.IBadge)
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

@component.adapter(interfaces.INTIIssuer)
@interface.implementer(open_interfaces.IVerificationObject)
def ntiissuer_to_mozilla_verification_object(issuer):
	verify = VerificationObject(type=open_interfaces.VO_TYPE_HOSTED,
								url=safestr(issuer.origin))
	return verify

@component.adapter(interfaces.INTIIssuer)
@interface.implementer(open_interfaces.IIssuerOrganization)
def ntiissuer_to_mozilla_issuer(issuer):
	result = IssuerOrganization(name=safestr(issuer.name),
						  		url=safestr(issuer.origin),
						  		email=issuer.email)
	return result

@component.adapter(interfaces.INTIBadge)
@interface.implementer(open_interfaces.IBadgeClass)
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

@component.adapter(interfaces.INTIAssertion)
@interface.implementer(open_interfaces.IBadgeAssertion)
def ntiassertion_to_mozilla_assertion(assertion):
	badge = assertion.badge
	issuer = badge.issuer
	issuedOn = assertion.issuedOn
	identity = assertion.recipient or assertion.person
	verify = open_interfaces.IVerificationObject(issuer)
	recipient = IdentityObject(identity=identity,
							   type=open_interfaces.ID_TYPE_EMAIL,
							   hashed=(assertion.salt is not None),
							   salt=assertion.salt)
	result = BadgeAssertion(uid=assertion.id,
							verify=verify,
							recipient=recipient,
							image=safestr(badge.image),
							badge=open_interfaces.IBadgeClass(badge),
							issuedOn=datetime.fromtimestamp(issuedOn))
	return result

@component.adapter(interfaces.INTIPerson)
@interface.implementer(tahrir_interfaces.IPerson)
def ntiperson_to_tahrir_person(nti):
	result = Person()
	result.email = safestr(nti.email)
	result.nickname = safestr(nti.name)
	result.bio = safestr(getattr(nti, "bio", None) or '')
	result.website = safestr(getattr(nti, "website", None) or '')
	result.created_on = datetime.fromtimestamp(nti.createdTime)
	return result

# mozilla->

@component.adapter(open_interfaces.IIdentityObject)
@interface.implementer(tahrir_interfaces.IPerson)
def mozilla_identity_object_to_tahrir_person(io):
	result = Person()
	result.email = safestr(io.identity)
	return result

@component.adapter(open_interfaces.IIssuerOrganization)
@interface.implementer(tahrir_interfaces.IIssuer)
def mozilla_issuer_to_tahrir_issuer(issuer):
	result = Issuer()
	result.org = safestr(issuer.url)
	result.name = safestr(issuer.name)
	result.origin = safestr(issuer.url)
	result.image = safestr(issuer.image)
	result.contact = safestr(issuer.email)
	return result

@component.adapter(open_interfaces.IIssuerOrganization)
@interface.implementer(interfaces.INTIIssuer)
def mozilla_issuer_to_ntiisuer(issuer):
	result = NTIIssuer(name=safestr(issuer.name),
					   origin=safestr(issuer.url),
					   email=safestr(issuer.email),
					   organization=safestr(issuer.url))
	return result

@component.adapter(open_interfaces.IIdentityObject)
@interface.implementer(interfaces.INTIPerson)
def mozilla_identityobject_to_ntiperson(iio):
	result = NTIPerson(email=safestr(iio.identity), name=safestr(iio.identity))
	return result

@component.adapter(open_interfaces.IBadgeClass)
@interface.implementer(tahrir_interfaces.IBadge)
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

@component.adapter(open_interfaces.IBadgeClass)
@interface.implementer(interfaces.INTIBadge)
def mozilla_badge_to_ntibadge(badge):
	# XXX: Issuer is not set
	result = NTIBadge(tags=badge.tags,
					  name=safestr(badge.name),
					  image=safestr(badge.image),
					  criteria=safestr(badge.criteria),
					  description=safestr(badge.description),
					  createdTime=time.time())
	return result
