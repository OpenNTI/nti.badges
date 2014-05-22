#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that
does_not = is_not

from zope import component

from nti.badges.tahrir import interfaces
from nti.badges.tahrir.manager import create_badge_manager
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