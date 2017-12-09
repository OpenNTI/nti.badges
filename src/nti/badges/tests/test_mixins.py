#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import assert_that
from hamcrest import has_property

import unittest

from nti.badges.mixins import ContentTypeAwareMixin


class TestMixins(unittest.TestCase):

    def test_mixin(self):
        class Foo(ContentTypeAwareMixin):
            pass
        assert_that(Foo(),
                    has_property('parameters', is_(dict)))
