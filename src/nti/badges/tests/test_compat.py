#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import assert_that

import unittest

from nti.badges._compat import bytes_


class TestCompat(unittest.TestCase):

    def test_bytes(self):
        assert_that(bytes_(u'data'), is_(b'data'))
        assert_that(bytes_(b'data'), is_(b'data'))
