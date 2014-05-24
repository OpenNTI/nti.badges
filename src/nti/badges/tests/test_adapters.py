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

from datetime import datetime

from tahrir_api.model import Badge, Person

from nti.badges import interfaces as badge_interfaces
from nti.badges.tahrir import interfaces as tahrir_interfaces
from nti.badges.openbadges import interfaces as open_interfaces

from nti.badges.tests import NTIBadgesTestCase

class TestAdapters(NTIBadgesTestCase):

	def test_tahrir_person_to_identity_object(self):
		person = Person()
		person.bio = 'I am foo'
		person.nickname = 'foo'
		person.email = u'foo@example.org'
		person.created_on = datetime.now()

		iio = open_interfaces.IIdentityObject(person, None)
		assert_that(iio, is_not(none()))
		assert_that(iio, has_property('identity', 'foo@example.org'))

	def test_tahrir_badge_to_ntibadge(self):
		badge = Badge()
		badge.name = u'fossbox'
		badge.created_on = datetime.now()
		badge.image = u'http://foss.rit.edu/files/fossboxbadge.png'
		badge.description = u'Welcome to the FOSSBox. A member is you!'
		badge.criteria = u'http://foss.rit.edu'

		ntibadge = badge_interfaces.INTIBadge(badge, None)
		assert_that(ntibadge, is_not(none()))
		assert_that(ntibadge, has_property('createdTime', is_not(none())))
		assert_that(ntibadge, has_property('name', 'fossbox'))
		assert_that(ntibadge, has_property('criteria', 'http://foss.rit.edu'))
		assert_that(ntibadge, has_property('image', 'http://foss.rit.edu/files/fossboxbadge.png'))
		assert_that(ntibadge, has_property('description', u'Welcome to the FOSSBox. A member is you!'))
