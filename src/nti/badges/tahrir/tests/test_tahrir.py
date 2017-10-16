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
does_not = is_not

from zope import component

from nti.badges.tahrir import get_tahrir_badge_by_id
from nti.badges.tahrir import get_tahrir_issuer_by_id
from nti.badges.tahrir import get_tahrir_person_by_id

from nti.badges.tahrir.interfaces import ITahrirBadgeManager

from nti.badges.tahrir.manager import create_badge_manager

from nti.badges.tests import NTIBadgesTestCase


class TestTahrir(NTIBadgesTestCase):

    def setUp(self):
        self.old = component.getUtility(ITahrirBadgeManager)
        self.new = create_badge_manager(dburi='sqlite://')
        component.provideUtility(self.new)

    def tearDown(self):
        component.provideUtility(self.old)

    def test_get_by_id(self):
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

        person_id = manager.db.add_person(email=u"person@site.com",
                                          nickname=u"person")

        issuer = get_tahrir_issuer_by_id(issuer_id)
        assert_that(issuer, is_not(none()))

        badge = get_tahrir_badge_by_id(badge_id)
        assert_that(badge, is_not(none()))

        person = get_tahrir_person_by_id(person_id)
        assert_that(person, is_not(none()))

        person = get_tahrir_person_by_id(person.id)
        assert_that(person, is_not(none()))
