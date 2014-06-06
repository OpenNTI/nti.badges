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

from . import interfaces
from .model import NTIBadge
from .model import NTIIssuer
from .model import NTIPerson
from .model import NTIAssertion

def _unicode(s):
	s = s.decode("utf-8") if isinstance(s, bytes) else s
	return unicode(s) if s is not None else None

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
								url=_unicode(issuer.origin))
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
	result = IssuerOrganization(url=_unicode(issuer.origin),
								name=_unicode(issuer.name),
								email=_unicode(issuer.contact),
								description=_unicode(issuer.org))
	return result

@component.adapter(tahrir_interfaces.IBadge)
@interface.implementer(open_interfaces.IBadgeClass)
def tahrir_badge_to_mozilla_badge(badge):
	tags = tuple(_unicode(x.lower()) for x in ((badge.tags or '').split(',')) if x)
	result = BadgeClass(tags=tags,
						name=_unicode(badge.name),
						image=_unicode(badge.image),
						criteria=_unicode(badge.criteria),
						issuer=_unicode(badge.issuer.origin),
						description=_unicode(badge.description))
	tag_badge_interfaces(badge, result)
	return result

@component.adapter(tahrir_interfaces.IAssertion)
@interface.implementer(open_interfaces.IBadgeAssertion)
def tahrir_assertion_to_mozilla_assertion(assertion):
	badge = assertion.badge
	# issuer
	issuer = badge.issuer
	verify = open_interfaces.IVerificationObject(issuer)
	# recipient
	salt = getattr(assertion, 'salt', None)
	identity = assertion.recipient if salt else assertion.person.email
	recipient = IdentityObject(salt=salt,
							   identity=identity,
							   hashed=(True if salt else False),
							   type=open_interfaces.ID_TYPE_EMAIL)
	# assertion
	aid = assertion.id or u"%s -> %s" % (badge.name, assertion.person.email)
	result = BadgeAssertion(uid=aid,
							verify=verify,
							recipient=recipient,
							image=_unicode(badge.image),
							issuedOn=assertion.issued_on,
							badge=open_interfaces.IBadgeClass(badge))
	return result

@component.adapter(tahrir_interfaces.IIssuer)
@interface.implementer(interfaces.INTIIssuer)
def tahrir_issuer_to_ntiissuer(issuer):
	result = NTIIssuer(name=_unicode(issuer.name),
					   origin=_unicode(issuer.origin),
					   email=_unicode(issuer.contact),
					   organization=_unicode(issuer.org),
					   createdTime=time.mktime(issuer.created_on.timetuple()))
	return result

@component.adapter(tahrir_interfaces.IBadge)
@interface.implementer(interfaces.INTIBadge)
def tahrir_badge_to_ntibadge(badge):
	tags = tuple(_unicode(x.lower()) for x in ((badge.tags or '').split(',')) if x)
	issuer = interfaces.INTIIssuer(badge.issuer, None)
	result = NTIBadge(issuer=issuer,
					  tags=tuple(tags),
					  name=_unicode(badge.name),
					  image=_unicode(badge.image),
					  criteria=_unicode(badge.criteria),
					  description=_unicode(badge.description),
					  createdTime=time.mktime(badge.created_on.timetuple()))
	return result

@component.adapter(tahrir_interfaces.IAssertion)
@interface.implementer(interfaces.INTIAssertion)
def tahrir_assertion_to_ntiassertion(ast):
	badge = interfaces.INTIBadge(ast.badge)
	interface.alsoProvides(badge, interfaces.IEarnedBadge)
	issuedOn = time.mktime(ast.issued_on.timetuple())
	result = NTIAssertion(badge=badge,
						  issuedOn=issuedOn,
						  person=_unicode(ast.person.email),
						  recipient=_unicode(ast.recipient),
						  salt=getattr(ast, 'salt', None))
	return result

@component.adapter(tahrir_interfaces.IPerson)
@interface.implementer(interfaces.INTIPerson)
def tahrir_person_to_ntiperson(person):
	assertions = [interfaces.INTIAssertion(x) for x in person.assertions]
	result = NTIPerson(name=_unicode(person.nickname),
					   email=_unicode(person.email),
					   assertions=assertions,
					   createdTime=time.mktime(person.created_on.timetuple()))
	# not part of the interface but keep them
	result.bio = _unicode(person.bio)
	result.website = _unicode(person.website)
	return result

# nti->

@component.adapter(interfaces.INTIIssuer)
@interface.implementer(tahrir_interfaces.IIssuer)
def ntiissuer_to_tahrir_issuer(issuer):
	result = Issuer()
	result.name = _unicode(issuer.name)
	result.contact = _unicode(issuer.email)
	result.origin = _unicode(issuer.origin)
	result.org = _unicode(issuer.organization)
	return result

@component.adapter(interfaces.INTIBadge)
@interface.implementer(tahrir_interfaces.IBadge)
def ntibadge_to_tahrir_badge(badge):
	# XXX: Issuer is not set
	tags = ','.join(badge.tags)
	result = Badge(tags=tags,
				   name=_unicode(badge.name),
				   image=_unicode(badge.image),
				   criteria=_unicode(badge.criteria),
				   description=_unicode(badge.description),
				   created_on=datetime.fromtimestamp(badge.createdTime))
	tag_badge_interfaces(badge, result)
	return result

@component.adapter(interfaces.INTIIssuer)
@interface.implementer(open_interfaces.IVerificationObject)
def ntiissuer_to_mozilla_verification_object(issuer):
	verify = VerificationObject(type=open_interfaces.VO_TYPE_HOSTED,
								url=_unicode(issuer.origin))
	return verify

@component.adapter(interfaces.INTIIssuer)
@interface.implementer(open_interfaces.IIssuerOrganization)
def ntiissuer_to_mozilla_issuer(issuer):
	result = IssuerOrganization(name=_unicode(issuer.name),
						  		url=_unicode(issuer.origin),
						  		email=issuer.email)
	return result

@component.adapter(interfaces.INTIBadge)
@interface.implementer(open_interfaces.IBadgeClass)
def ntibadge_to_mozilla_badge(badge):
	issuer = badge.issuer
	result = BadgeClass(tags=badge.tags,
						name=_unicode(badge.name),
						image=_unicode(badge.image),
						issuer=_unicode(issuer.origin),
						description=badge.description,
						criteria=_unicode(badge.criteria))
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
	result = BadgeAssertion(uid=badge.name,
							verify=verify,
							recipient=recipient,
							image=_unicode(badge.image),
							badge=open_interfaces.IBadgeClass(badge),
							issuedOn=datetime.fromtimestamp(issuedOn))
	return result

@component.adapter(interfaces.INTIPerson)
@interface.implementer(tahrir_interfaces.IPerson)
def ntiperson_to_tahrir_person(nti):
	result = Person()
	result.email = _unicode(nti.email)
	result.nickname = _unicode(nti.name)
	result.bio = _unicode(getattr(nti, "bio", None) or '')
	result.website = _unicode(getattr(nti, "website", None) or '')
	result.created_on = datetime.fromtimestamp(nti.createdTime)
	return result

# mozilla->

@component.adapter(open_interfaces.IIdentityObject)
@interface.implementer(tahrir_interfaces.IPerson)
def mozilla_identity_object_to_tahrir_person(io):
	result = Person()
	result.email = _unicode(io.identity)
	return result

@component.adapter(open_interfaces.IIssuerOrganization)
@interface.implementer(tahrir_interfaces.IIssuer)
def mozilla_issuer_to_tahrir_issuer(issuer):
	result = Issuer()
	result.org = _unicode(issuer.url)
	result.name = _unicode(issuer.name)
	result.origin = _unicode(issuer.url)
	result.image = _unicode(issuer.image)
	result.contact = _unicode(issuer.email)
	return result

@component.adapter(open_interfaces.IIssuerOrganization)
@interface.implementer(interfaces.INTIIssuer)
def mozilla_issuer_to_ntiisuer(issuer):
	result = NTIIssuer(name=_unicode(issuer.name),
					   origin=_unicode(issuer.url),
					   email=_unicode(issuer.email),
					   organization=_unicode(issuer.url))
	return result

@component.adapter(open_interfaces.IIdentityObject)
@interface.implementer(interfaces.INTIPerson)
def mozilla_identityobject_to_ntiperson(iio):
	result = NTIPerson(email=_unicode(iio.identity), name=_unicode(iio.identity))
	return result

@component.adapter(open_interfaces.IBadgeClass)
@interface.implementer(tahrir_interfaces.IBadge)
def mozilla_badge_to_tahrir_badge(badge):
	# XXX: Issuer is not set
	result = Badge()
	result.name = _unicode(badge.name)
	result.image = _unicode(badge.image)
	result.criteria = _unicode(badge.criteria)
	result.tags = u','.join(badge.tags)
	result.description = _unicode(badge.description)
	tag_badge_interfaces(badge, result)
	return result

@component.adapter(open_interfaces.IBadgeClass)
@interface.implementer(interfaces.INTIBadge)
def mozilla_badge_to_ntibadge(badge):
	# XXX: Issuer is not set
	result = NTIBadge(tags=badge.tags,
					  name=_unicode(badge.name),
					  image=_unicode(badge.image),
					  criteria=_unicode(badge.criteria),
					  description=_unicode(badge.description),
					  createdTime=time.time())
	return result
