#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import has_properties

import unittest

import fudge

from zope.dottedname import resolve as dottedname


class TestInterfaces(unittest.TestCase):

    def test_import_interfaces(self):
        dottedname.resolve('nti.badges.openbadges.interfaces')

    def test_event(self):
        from nti.badges.openbadges.interfaces import BadgeAwardedEvent
        event = BadgeAwardedEvent(fudge.Fake(), 'aizen')
        assert_that(event,
                    has_properties('assertion', is_not(none()),
                                   'creator', 'aizen'))
