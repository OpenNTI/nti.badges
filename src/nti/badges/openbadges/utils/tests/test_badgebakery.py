#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import equal_to
from hamcrest import assert_that
does_not = is_not

import os
from cStringIO import StringIO
       
from nti.badges.openbadges.utils import load_data
from nti.badges.openbadges.utils.badgebakery import get_baked_data, bake_badge

from nti.badges.tests import NTIBadgesTestCase

class TestBadgeBakery(NTIBadgesTestCase):

    def test_png_url(self):
        path = os.path.join(os.path.dirname(__file__), 'ichigo.png')
        with open(path, "rb") as fp:
            PNG = fp.read()
    
        unbaked = StringIO(PNG)
        assert_that(get_baked_data(unbaked), is_(none()))

        baked = StringIO()
        unbaked = StringIO(PNG)
        bake_badge(unbaked, baked, url='http://foo.org/assertion.json')

        baked = StringIO(baked.getvalue())
        assert_that(get_baked_data(baked), is_('http://foo.org/assertion.json'))

        rebaked = StringIO()
        baked = StringIO(baked.getvalue())
        bake_badge(baked, rebaked, 'http://another/assertion')

        rebaked = StringIO(rebaked.getvalue())
        assert_that(get_baked_data(rebaked), is_('http://another/assertion'))

    def test_png_payload(self):
        path = os.path.join(os.path.dirname(__file__), 'ichigo.png')
        with open(path, "rb") as fp:
            PNG = fp.read()
    
        baked = StringIO()
        unbaked = StringIO(PNG)
        payload = {'manga': 'bleach'}
        bake_badge(unbaked, baked, payload=payload)

        baked = StringIO(baked.getvalue())
        baked_data = get_baked_data(baked)
        assert_that(baked_data, is_not(none()))
        baked_data = load_data(baked_data)
        assert_that(baked_data, is_(equal_to(payload)))
