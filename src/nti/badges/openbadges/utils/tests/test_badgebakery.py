#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import raises
from hamcrest import calling
from hamcrest import equal_to
from hamcrest import assert_that
does_not = is_not

import os
import shutil
import tempfile
from io import BytesIO

from nti.badges.openbadges.utils import load_data

from nti.badges.openbadges.utils.badgebakery import bake_badge
from nti.badges.openbadges.utils.badgebakery import process_args
from nti.badges.openbadges.utils.badgebakery import get_baked_data

from nti.badges.tests import NTIBadgesTestCase


class TestBadgeBakery(NTIBadgesTestCase):

    def test_png_url(self):
        path = os.path.join(os.path.dirname(__file__), 'ichigo.png')
        with open(path, "rb") as fp:
            PNG = fp.read()

        unbaked = BytesIO(PNG)
        assert_that(get_baked_data(unbaked), is_(none()))

        baked = BytesIO()
        unbaked = BytesIO(PNG)
        bake_badge(unbaked, baked, url='http://foo.org/assertion.json')

        baked = BytesIO(baked.getvalue())
        assert_that(get_baked_data(baked),
                    is_('http://foo.org/assertion.json'))

        baked = BytesIO(baked.getvalue())
        assert_that(get_baked_data(baked, raw=True),
                    is_('http://foo.org/assertion.json'))

        rebaked = BytesIO()
        baked = BytesIO(baked.getvalue())
        bake_badge(baked, rebaked, 'http://another/assertion')

        rebaked = BytesIO(rebaked.getvalue())
        assert_that(get_baked_data(rebaked), is_('http://another/assertion'))

    def test_coverage(self):
        path = os.path.join(os.path.dirname(__file__), 'ichigo.png')
        with open(path, "rb") as fp:
            PNG = fp.read()

        baked = BytesIO()
        unbaked = BytesIO(PNG)
        bake_badge(unbaked, baked, payload='asserted')
        assert_that(get_baked_data(baked),
                    is_('asserted'))

        baked = BytesIO()
        unbaked = BytesIO(PNG)
        bake_badge(unbaked, baked, payload='asserted', secret='123')
        assert_that(get_baked_data(baked),
                    is_(none()))

        assert_that(get_baked_data(baked, secret='1234'),
                    is_(none()))

        assert_that(get_baked_data(baked, secret='123'),
                    is_('asserted'))

        baked = BytesIO()
        unbaked = BytesIO(PNG)
        assert_that(calling(bake_badge).with_args(unbaked, baked, 'http://example/i.json', 'asserted'),
                    raises(ValueError))

    def test_process_args(self):
        img_dir = tempfile.mkdtemp(dir="/tmp")
        try:
            # prepare issuer
            path = os.path.join(os.path.dirname(__file__), 'ichigo.png')
            shutil.copy(path, os.path.join(img_dir, 'ichigo.png'))
            path = os.path.join(img_dir, 'ichigo.png')
            assert_that(process_args(['-v', img_dir + '/foo.png']),
                        is_(2))

            assertion = os.path.join(os.path.dirname(__file__), 
                                     'assertion4.json')
            assert_that(process_args(['-v', '-p', assertion, img_dir + '/ichigo.png']),
                        is_(2))

            assertion = os.path.join(os.path.dirname(__file__), 
                                     'assertion.json')
            assert_that(process_args(['-v', '-p', assertion, img_dir + '/ichigo.png']),
                        is_(0))
        finally:
            shutil.rmtree(img_dir, True)

    def test_png_payload(self):
        path = os.path.join(os.path.dirname(__file__), 'ichigo.png')
        with open(path, "rb") as fp:
            PNG = fp.read()

        baked = BytesIO()
        unbaked = BytesIO(PNG)
        payload = {'manga': 'bleach'}
        bake_badge(unbaked, baked, payload=payload)

        baked = BytesIO(baked.getvalue())
        baked_data = get_baked_data(baked)
        assert_that(baked_data, is_not(none()))
        baked_data = load_data(baked_data)
        assert_that(baked_data, is_(equal_to(payload)))
