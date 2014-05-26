#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

import time
from datetime import datetime

from tahrir_api.model import Badge, Person, Issuer

from nti.badges.model import NTIIssuer
from nti.badges.model import NTIPerson
from nti.badges import interfaces as badge_interfaces
from nti.badges.tahrir import interfaces as tahrir_interfaces
from nti.badges.openbadges import interfaces as open_interfaces

from nti.badges.tests import NTIBadgesTestCase

class TestAdapters(NTIBadgesTestCase):

	# Tahrir

	def test_tahrir_person_to_identity_object(self):
		person = Person()
		person.bio = 'I am foo'
		person.nickname = 'foo'
		person.email = u'foo@example.org'
		person.created_on = datetime.now()

		iio = open_interfaces.IIdentityObject(person, None)
		assert_that(iio, is_not(none()))
		assert_that(iio, has_property('identity', 'foo@example.org'))

	def test_tahrir_issuer_to_mozilla_issuer(self):
		issuer = Issuer()
		issuer.name = 'foo'
		issuer.org = u'http://example.org'
		issuer.contact = u'foo@example.org'
		issuer.origin = 'http://example.org/foo'

		nti = open_interfaces.IIssuerOrganization(issuer, None)
		assert_that(nti, is_not(none()))
		assert_that(nti, has_property('name', 'foo'))
		assert_that(nti, has_property('email', 'foo@example.org'))
		assert_that(nti, has_property('url', 'http://example.org/foo'))
		assert_that(nti, has_property('description', 'http://example.org'))

	def test_tahrir_person_to_ntiperson(self):
		person = Person()
		person.bio = 'I am foo'
		person.nickname = 'foo'
		person.email = u'foo@example.org'
		person.created_on = datetime.now()

		nti = badge_interfaces.INTIPerson(person, None)
		assert_that(nti, is_not(none()))
		assert_that(nti, has_property('name', 'foo'))
		assert_that(nti, has_property('email', 'foo@example.org'))
		assert_that(nti, has_property('createdTime', is_not(none())))

	def test_tahrir_issuer_to_ntiissuer(self):
		issuer = Issuer()
		issuer.name = 'foo'
		issuer.org = u'http://example.org'
		issuer.contact = u'foo@example.org'
		issuer.origin = 'http://example.org/foo'

		nti = badge_interfaces.INTIIssuer(issuer, None)
		assert_that(nti, is_not(none()))
		assert_that(nti, has_property('uri', 'foo'))
		assert_that(nti, has_property('email', 'foo@example.org'))
		assert_that(nti, has_property('origin', 'http://example.org/foo'))
		assert_that(nti, has_property('organization', 'http://example.org'))

	def test_tahrir_badge_to_ntibadge(self):
		badge = Badge()
		badge.name = u'fossbox'
		badge.tags = "fox,box,"
		badge.created_on = datetime.now()
		badge.criteria = u'http://foss.rit.edu'
		badge.image = u'http://foss.rit.edu/files/fossboxbadge.png'
		badge.description = u'Welcome to the FOSSBox. A member is you!'

		nti = badge_interfaces.INTIBadge(badge, None)
		assert_that(nti, is_not(none()))
		assert_that(nti, has_property('name', 'fossbox'))
		assert_that(nti, has_property('tags', is_(('fox', 'box'))))
		assert_that(nti, has_property('createdTime', is_not(none())))
		assert_that(nti, has_property('criteria', 'http://foss.rit.edu'))
		assert_that(nti, has_property('image', 'http://foss.rit.edu/files/fossboxbadge.png'))
		assert_that(nti, has_property('description', u'Welcome to the FOSSBox. A member is you!'))

	# NTI

	def test_ntiperson_to_tahrir_person(self):
		person = NTIPerson()
		person.name = 'foo'
		person.bio = 'I am foo'
		person.createdTime = time.time()
		person.email = u'foo@example.org'
		person.website = u'http://example.org/foo'

		tah = tahrir_interfaces.IPerson(person, None)
		assert_that(tah, is_not(none()))
		assert_that(tah, has_property('nickname', 'foo'))
		assert_that(tah, has_property('bio', 'I am foo'))
		assert_that(tah, has_property('email', 'foo@example.org'))
		assert_that(tah, has_property('created_on', is_not(none())))
		assert_that(tah, has_property('website', u'http://example.org/foo'))

	def test_ntiissuer_to_mozilla_issuer(self):
		person = NTIIssuer()
		person.uri = 'foo'
		person.email = u'foo@example.org'
		person.origin = 'http://example.org/foo'
		person.organization = 'http://example.org'

		io = open_interfaces.IIssuerOrganization(person, None)
		assert_that(io, is_not(none()))
		assert_that(io, has_property('name', 'foo'))
		assert_that(io, has_property('email', 'foo@example.org'))
		assert_that(io, has_property('url', 'http://example.org/foo'))
