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
does_not = is_not

import os
from cStringIO import StringIO
       
from nti.badges.openbadges.utils.badgebakery import get_baked_url, bake_badge

from nti.badges.tests import NTIBadgesTestCase

class TestBadgeBakery(NTIBadgesTestCase):

    def test_png(self):
        path = os.path.join(os.path.dirname(__file__), 'ichigo.png')
        with open(path, "rb") as fp:
            PNG = fp.read()
    
        unbaked = StringIO(PNG)
        assert_that(get_baked_url(unbaked), is_(none()))

        baked = StringIO()
        unbaked = StringIO(PNG)
        bake_badge(unbaked, baked, 'http://foo.org/assertion.json')

        baked = StringIO(baked.getvalue())
        assert_that(get_baked_url(baked), is_('http://foo.org/assertion.json'))

        rebaked = StringIO()
        baked = StringIO(baked.getvalue())
        bake_badge(baked, rebaked, 'http://another/assertion')

        rebaked = StringIO(rebaked.getvalue())
        assert_that(get_baked_url(rebaked), is_('http://another/assertion'))
