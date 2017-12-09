#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import assert_that

from nti.badges.tahrir.dbapi import hexdigest

from nti.badges.tests import NTIBadgesTestCase


class TestDBApi(NTIBadgesTestCase):

    def test_hexdigest(self):
        assert_that(hexdigest(b'foxbot'),
                    is_('e6fb34ff426220fb8b65735824b7416cc375c25d464afce827406e08ca9c9c6d'))
