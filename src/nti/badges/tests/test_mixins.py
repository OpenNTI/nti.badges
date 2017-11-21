#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

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
