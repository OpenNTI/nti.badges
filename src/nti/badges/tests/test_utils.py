#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import assert_that
from hamcrest import has_property

import unittest

import six

from nti.badges.utils import MetaBadgeObject


class TestUtils(unittest.TestCase):

    def test_meta_class(self):
        @six.add_metaclass(MetaBadgeObject)
        class Foo(object):
            pass
        assert_that(Foo(),
                    has_property('mimeType', 'application/vnd.nextthought.badges.foo'))
