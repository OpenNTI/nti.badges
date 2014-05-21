#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

# from hamcrest import is_not
# from hamcrest import assert_that
# from hamcrest import has_property
# does_not = is_not
#
# from tahrir_api.model import Badge
#
# from nti.badges.tests import NTIBadgesTestCase
#
# class TestAdapters(NTIBadgesTestCase):
#
# 	def test_tahrir_badge_to_open_badge(self):
# 		badge = Badge()
# 		badge.name = u'fossbox'
# 		badge.image = u'http://foss.rit.edu/files/fossboxbadge.png'
# 		badge.description = u'Welcome to the FOSSBox. A member is you!'
# 		badge.criteria = u'http://foss.rit.edu'
# 		openbadge = tahrir_badge_to_open_badge(badge, 'http://issuer.json')
# 		assert_that(openbadge, has_property('name','fossbox'))
# 		assert_that(openbadge, has_property('description',u'Welcome to the FOSSBox. A member is you!'))
# 		assert_that(openbadge, has_property('image','http://foss.rit.edu/files/fossboxbadge.png'))
# 		assert_that(openbadge, has_property('criteria','http://foss.rit.edu'))
