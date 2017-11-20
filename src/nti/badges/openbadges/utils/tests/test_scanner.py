#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import ends_with
from hamcrest import has_length
from hamcrest import assert_that
does_not = is_not

from nti.testing.matchers import verifiably_provides

import os
import shutil
import tempfile

import simplejson

from nti.badges.openbadges import interfaces

from nti.badges.openbadges.utils.badgebakery import bake_badge

from nti.badges.openbadges.utils.scanner import flat_scan
from nti.badges.openbadges.utils.scanner import parse_badge
from nti.badges.openbadges.utils.scanner import parse_issuer
from nti.badges.openbadges.utils.scanner import get_baked_data
from nti.badges.openbadges.utils.scanner import get_issuer_url

from nti.badges.tests import NTIBadgesTestCase


class TestScanner(NTIBadgesTestCase):

    def test_scan(self):
        img_dir = tempfile.mkdtemp(dir="/tmp")
        try:
            # prepare issuer
            issuer_json = os.path.join(os.path.dirname(__file__),
                                       'issuer.json')
            shutil.copy(issuer_json, os.path.join(img_dir, 'issuer.json'))

            assert_that(parse_issuer(img_dir),
                        is_(none()))

            issuer = parse_issuer(issuer_json, True)
            assert_that(issuer,
                        is_not(none()))

            assert_that(get_issuer_url('https://example.com'),
                        is_('https://example.com'))

            assert_that(get_issuer_url(issuer),
                        is_('https://example.org'))

            class FakeIssuer(object):
                def __str__(self):
                    return "https://example.io"

            assert_that(get_issuer_url(FakeIssuer()),
                        is_('https://example.io'))
            # prepare badge
            badge_json = os.path.join(os.path.dirname(__file__), 'badge.json')
            with open(badge_json, "rb") as fp:
                badge = simplejson.load(fp, 'utf-8')
                badge['issuer'] = 'file://' + os.path.join(img_dir, 'issuer.json')

            badge_json = os.path.join(img_dir, 'badge.json')
            with open(badge_json, "w") as fp:
                simplejson.dump(badge, fp)

            badge2_json = os.path.join(os.path.dirname(__file__), 
                                       'nti_badge.json')
            shutil.copy(badge2_json, img_dir + "/nti_badge.json")

            # bake image
            ichigo_png = os.path.join(os.path.dirname(__file__), 'ichigo.png')
            out_ichigo = os.path.join(img_dir, 'ichigo.png')
            bake_badge(ichigo_png, out_ichigo,
                       url='file://' + os.path.join(img_dir, 'badge.json'))

            assert_that(get_baked_data(badge_json),
                        is_(none()))

            data = get_baked_data(out_ichigo)
            assert_that(data, ends_with('badge.json'))

            assert_that(parse_badge(ichigo_png),
                        is_(none()))

            assert_that(parse_badge(data, True),
                        is_not(none()))

            results = flat_scan(img_dir, True)
            assert_that(results, has_length(2))

            data = results[0]
            assert_that(data, has_length(2))

            badge = data[0]
            assert_that(badge, verifiably_provides(interfaces.IBadgeClass))

            issuer = data[1]
            assert_that(issuer,
                        verifiably_provides(interfaces.IIssuerOrganization))
        finally:
            shutil.rmtree(img_dir)
