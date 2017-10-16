#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

from zope import component

from nti.badges.openbadges import interfaces as open_interfaces

from nti.badges.tahrir import get_tahrir_badge_by_id

from nti.badges.tahrir import interfaces as tahrir_interfaces

from nti.badges.tahrir.manager import create_badge_manager

from nti.badges.tests import NTIBadgesTestCase


class TestTahrirAdapters(NTIBadgesTestCase):

    def setUp(self):
        self.old = component.getUtility(tahrir_interfaces.ITahrirBadgeManager)
        self.new = create_badge_manager(dburi='sqlite://')
        component.provideUtility(self.new)

    def tearDown(self):
        component.provideUtility(self.old)

    def test_adapters(self):
        manager = self.new
        assert_that(manager, is_not(none()))

        issuer_id = manager.db.add_issuer(u'http://foss.rit.edu/badges',
                                          u'FOSS@RIT',
                                          u'http://foss.rit.edu', u'foss@rit.edu')

        badge_id = manager.db.add_badge(name=u'fossbox',
                                        image=u'http://foss.rit.edu/files/fossboxbadge.png',
                                        desc=u'Welcome to the FOSSBox. A member is you!',
                                        criteria=u'http://foss.rit.edu',
                                        issuer_id=issuer_id)

        manager.db.add_person(email=u"person@site.com", nickname=u"person")
        manager.add_assertion(u"person@site.com", u'fossbox', issued_on=None)

        badge = get_tahrir_badge_by_id(badge_id)
        open_badge = open_interfaces.IBadgeClass(badge, None)
        assert_that(open_badge, is_not(none()))
        assert_that(open_badge, has_property('issuer',
                                             has_property('url', 'http://foss.rit.edu/badges')))

        assertion = manager.get_assertion("person@site.com", 'fossbox')
        open_assertion = open_interfaces.IBadgeAssertion(assertion, None)
        assert_that(open_assertion, is_not(none()))
