#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

from datetime import datetime

from zope import component

from tahrir_api.model import Badge, Person, Issuer

from nti.badges.tahrir import interfaces
from nti.badges import interfaces as badge_interfaces
from nti.badges.tahrir.manager import create_badge_manager
from nti.badges.openbadges import interfaces as open_interfaces

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans

from nti.badges.tests import NTIBadgesTestCase

class TestTahrirBadgeManager(NTIBadgesTestCase):

	def test_registration(self):
		manager = component.queryUtility(interfaces.ITahrirBadgeManager)
		assert_that(manager, is_not(none()))
		
	@WithMockDSTrans
	def test_fossboxbadge(self):
		manager = create_badge_manager(dburi="sqlite://")
		assert_that(manager, is_not(none()))

		issuer_id = manager.db.add_issuer(u'http://foss.rit.edu/badges',
										  u'FOSS@RIT',
										  u'http://foss.rit.edu', u'foss@rit.edu')
		assert_that(issuer_id, is_not(none()))

		badge = manager.db.add_badge(
					u'fossbox',
					u'http://foss.rit.edu/files/fossboxbadge.png',
					u'Welcome to the FOSSBox. A member is you!',
					u'http://foss.rit.edu', issuer_id)
		assert_that(badge, is_not(none()))

	def _test_nti_assertion(self, assertion):
		nti = badge_interfaces.INTIAssertion(assertion, None)
		assert_that(nti, is_not(none()))
		assert_that(nti, has_property('badge', is_not(none())))
		assert_that(nti, has_property('issuedOn', is_not(none())))
		assert_that(nti, has_property('recipient', is_('foo@example.org')))

	def _test_open_assertion(self, assertion):
		ast = open_interfaces.IBadgeAssertion(assertion, None)
		assert_that(ast, is_not(none()))
		assert_that(ast, has_property('uid', is_('fossbox')))
		assert_that(ast, has_property('image', is_('http://foss.rit.edu/files/fossboxbadge.png')))
		assert_that(ast, has_property('recipient', has_property('identity', 'foo@example.org')))
		assert_that(ast, has_property('badge', has_property('name', 'fossbox')))
		assert_that(ast, has_property('verify', has_property('url', 'http://foss.rit.edu/badges')))

	def _test_open_badge(self, badge):
		ob = open_interfaces.IBadgeClass(badge, None)
		assert_that(ob, is_not(none()))
		assert_that(ob, has_property('name', 'fossbox'))
		assert_that(ob, has_property('tags', is_((u'fox', u'box'))))
		assert_that(ob, has_property('criteria', 'http://foss.rit.edu'))
		assert_that(ob, has_property('image', 'http://foss.rit.edu/files/fossboxbadge.png'))
		assert_that(ob, has_property('description', u'Welcome to the FOSSBox. A member is you!'))

	@WithMockDSTrans
	def test_operations(self):
		manager = create_badge_manager(dburi="sqlite://")

		issuer = Issuer()
		issuer.name = u'FOSS@RIT'
		issuer.origin = u'http://foss.rit.edu/badges'
		issuer.org = u'http://foss.rit.edu'
		issuer.contact = u'foss@rit.edu'
		issuer_id = manager.add_issuer(issuer)
		assert_that(issuer_id, is_not(none()))

		assert_that(manager.get_issuer('FOSS@RIT', u'http://foss.rit.edu/badges'), is_not(none()))

		badge = Badge()
		badge.name = u'fossbox'
		badge.criteria = u'http://foss.rit.edu'
		badge.description = u'Welcome to the FOSSBox. A member is you!'
		badge.tags = 'fox,box,'
		badge.issuer_id = issuer_id
		badge.image = u'http://foss.rit.edu/files/fossboxbadge.png'
		badge_id = manager.add_badge(badge)
		assert_that(badge_id, is_not(badge))

		db_badge = manager.get_badge(u'fossbox')
		assert_that(db_badge, is_not(none()))
		self._test_open_badge(db_badge)

		person = Person()
		person.bio = 'I am foo'
		person.nickname = 'foo'
		person.email = u'foo@example.org'
		person.created_on = datetime.now()
		person.website = 'http://example.org/foo'

		pid = manager.add_person(person)
		assert_that(pid, is_('foo@example.org'))

		person = manager.get_person(email=pid)
		assert_that(person, has_property('bio', 'I am foo'))
		assert_that(person, has_property('website', 'http://example.org/foo'))

		assert_that(manager.person_exists(email='foo@example.org'), is_(True))

		assert_that(manager.add_assertion('foo@example.org', 'fossbox'), is_not(False))
		assertion = manager.get_assertion('foo@example.org', 'fossbox')
		assert_that(assertion, is_not(none()))
		assert_that(manager.assertion_exists('foo@example.org', 'fossbox'), is_(True))
		self._test_nti_assertion(assertion)
		self._test_open_assertion(assertion)

		badge = manager.get_badge('fossbox')
		assert_that(badge, is_not(none()))

		badges = manager.get_all_badges()
		assert_that(badges, has_length(1))

		badges = manager.get_person_badges('foo@example.org')
		assert_that(badges, has_length(1))

		assertions = manager.get_person_assertions('foo@example.org')
		assert_that(assertions, has_length(1))
		
		assert_that(manager.delete_person(pid), is_('foo@example.org'))
