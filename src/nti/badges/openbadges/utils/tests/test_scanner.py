#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import is_not
from hamcrest import has_length
from hamcrest import assert_that
does_not = is_not

import os
import shutil
import tempfile
import simplejson

from nti.badges.openbadges import interfaces
from nti.badges.openbadges.utils.scanner import flat_scan
from nti.badges.openbadges.utils.badgebakery import bake_badge

from nti.badges.tests import NTIBadgesTestCase

class TestBadgeBakery(NTIBadgesTestCase):

	def test_scan(self):
		img_dir = tempfile.mkdtemp(dir="/tmp")
		try:
			# prepare issuer
			issuer_json = os.path.join(os.path.dirname(__file__), 'issuer.json')
			shutil.copy(issuer_json, os.path.join(img_dir, 'issuer.json'))

			# prepare batch
			badge_json = os.path.join(os.path.dirname(__file__), 'badge.json')
			with open(badge_json, "rb") as fp:
				badge = simplejson.load(fp)
				badge['issuer'] = 'file://' + os.path.join(img_dir, 'issuer.json')

			badge_json = os.path.join(img_dir, 'badge.json')
			with open(badge_json, "wb") as fp:
				simplejson.dump(badge, fp)

			# bake image
			ichigo_png = os.path.join(os.path.dirname(__file__), 'ichigo.png')
			out_ichigo = os.path.join(img_dir, 'ichigo.png')
			bake_badge(ichigo_png, out_ichigo, 'file://' + os.path.join(img_dir, 'badge.json'))

			results = flat_scan(img_dir, True)
			assert_that(results, has_length(1))
			assert_that(results[0], has_length(2))
			assert_that(interfaces.IBadgeClass.providedBy(results[0][0]), is_(True))
			assert_that(interfaces.IIssuerOrganization.providedBy(results[0][1]), is_(True))
		finally:
			shutil.rmtree(img_dir)