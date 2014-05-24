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

from ._compact import navstr

from .openbadges.model import BadgeClass
from .openbadges.model import IssuerObject
from .openbadges.model import BadgeAssertion
from .openbadges.model import IdentityObject
from .openbadges.model import VerificationObject
from .openbadges import interfaces as open_interfaces

from .tahrir import interfaces as tahrir_interfaces

from . import interfaces
from .model import NTIBadge
from .model import NTIIssuer
from .model import NTIPerson
from .model import NTIAssertion

def tag_badge_interfaces(source, target):
	if interfaces.IEarnableBadge.providedBy(source):
		interface.alsoProvides(target, interfaces.IEarnableBadge)

	if interfaces.IEarnedBadge.providedBy(source):
		interface.alsoProvides(target, interfaces.IEarnedBadge)

# tahrir->

@component.adapter(tahrir_interfaces.IPerson)
@interface.implementer(open_interfaces.IIdentityObject)
def tahrir_person_to_identity_object(person):
	result = IdentityObject(identity=person.email,
							type=open_interfaces.ID_TYPE_EMAIL,
							hashed=False,
							salt=None)
	return result

@component.adapter(tahrir_interfaces.IIssuer)
@interface.implementer(interfaces.INTIIssuer)
def tahrir_issuer_to_ntiissuer(issuer):
	result = NTIIssuer(uri=issuer.name,
					   origin=issuer.origin,
					   organization=issuer.org,
					   email=issuer.contact)
	return result

@component.adapter(tahrir_interfaces.IBadge)
@interface.implementer(interfaces.INTIBadge)
def tahrir_badge_to_ntibadge(badge):
	tags = tuple(x.lower() for x in ((badge.tags or u'').split(',')))
	issuer = interfaces.INTIIssuer(badge.issuer, None)
	result = NTIBadge(tags=tags,
					  name=badge.name,
					  image=badge.image,
					  criteria=badge.criteria,
					  description=badge.description,
					  createdTime=time.mktime(badge.created_on.timetuple()))
	if issuer is not None:
		result.issuer = issuer
	return result

@component.adapter(tahrir_interfaces.IAssertion)
@interface.implementer(interfaces.INTIAssertion)
def tahrir_assertion_to_ntiassertion(ast):
	badge = interfaces.INTIBadge(ast.badge, None)
	if badge is not None:
		interface.alsoProvides(badge, interfaces.IEarnedBadge)
	issuedOn = time.mktime(ast.issued_on.timetuple())
	assertion = NTIAssertion(badge=badge,
							 issueOn=issuedOn,
							 recipient=ast.recipient)
	return assertion

@component.adapter(tahrir_interfaces.IPerson)
@interface.implementer(interfaces.INTIPerson)
def tahrir_person_to_ntiperson(person):
	assertions = [interfaces.INTIAssertion(x) for x in person.assertions]
	result = NTIPerson(name=person.nickname,
					   email=person.email,
					   assertions=assertions,
					   createdTime=time.mktime(person.created_on.timetuple()))
	return result

# mozilla->

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
	result.name = issuer.name
	result.origin = issuer.url
	result.image = issuer.image
	result.contact = issuer.email
	return result

@component.adapter(open_interfaces.IBadgeClass)
@interface.implementer(tahrir_interfaces.IBadge)
def mozilla_badge_to_tahrir_badge(badge):
	# Issuer is not set
	result = Badge()
	result.name = badge.name
	result.image = badge.image
	result.criteria = badge.criteria
	result.description = badge.description
	tag_badge_interfaces(badge, result)
	return result

@component.adapter(open_interfaces.IIssuerObject)
@interface.implementer(interfaces.INTIIssuer)
def mozilla_badge_to_ntiisuer(issuer):
	result = NTIIssuer(uri=issuer.name,
					   origin=issuer.url,
					   email=issuer.email,
					   organization=issuer.url)
	return result

@component.adapter(open_interfaces.IIdentityObject)
@interface.implementer(interfaces.INTIPerson)
def mozilla_identityobject_to_ntiperson(iio):
	result = NTIPerson(email=iio.identity, name=iio.identity)
	return result
	
@component.adapter(open_interfaces.IBadgeClass)
@interface.implementer(interfaces.INTIBadge)
def mozilla_badge_to_ntibadge(badge):
	# Issuer not set
	result = NTIBadge(tags=(),
					  name=badge.name,
					  image=badge.image,
					  criteria=badge.criteria,
					  description=badge.description,
					  createdTime=time.time())
	return result

# nti->

@component.adapter(interfaces.INTIIssuer)
@interface.implementer(tahrir_interfaces.IIssuer)
def ntiissuer_to_tahrir_issuer(issuer):
	result = Issuer()
	result.name = issuer.uri
	result.contact = issuer.email
	result.origin = issuer.origin
	result.org = issuer.organization
	return result

@component.adapter(interfaces.INTIBadge)
@interface.implementer(tahrir_interfaces.IBadge)
def ntibadge_to_tahrir_badge(badge):
	# Issuer not set
	tags = ','.join(badge.tags)
	result = Badge(tags=tags,
				   name=badge.name,
				   image=badge.image,
				   criteria=badge.criteria,
				   description=badge.description,
				   created_on=datetime.fromtimestamp(badge.createdTime))
	tag_badge_interfaces(badge, result)
	return result

@component.adapter(interfaces.INTIIssuer)
@interface.implementer(open_interfaces.IIssuerObject)
def ntiissuer_to_mozilla_issuer(issuer):
	result = IssuerObject(name=issuer.uri,
						  url=issuer.origin,
						  email=issuer.email)
	return result

@component.adapter(interfaces.INTIBadge)
@interface.implementer(open_interfaces.IBadgeClass)
def ntibadge_to_mozilla_badge(badge):
	issuer = badge.issuer
	result = BadgeClass(tags=badge.tags,
						name=badge.name,
						image=badge.image,
						issuer=navstr(issuer.origin),
						description=badge.description,
						criteria=navstr(badge.criteria))
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
