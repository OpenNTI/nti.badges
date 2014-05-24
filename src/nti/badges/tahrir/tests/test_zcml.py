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
from hamcrest import has_property

from zope import component

from nti.badges.tahrir.interfaces import IIssuer
from nti.badges.tahrir.interfaces import ITahrirBadgeManager

import nti.testing.base

ZCML_STRING = """
<configure 	xmlns="http://namespaces.zope.org/zope"
			xmlns:zcml="http://namespaces.zope.org/zcml"
			xmlns:tdb="http://nextthought.com/ntp/tahrir"
			i18n_domain='nti.dataserver'>

	<include package="zope.component" />
	<include package="zope.annotation" />
	<include package="z3c.baseregistry" file="meta.zcml" />
	<include package="." file="meta.zcml" />

	<tdb:registerTahrirDB defaultSQLite="True" />

	<tdb:registerTahrirIssuer
				id="NTI"
			 	name="NextThought"
			 	org="http://www.nextthought.com"
			 	contact="contact@nextthought.com"
			 	origin="http://www.nextthought.com"/>
</configure>
"""

class TestZcml(nti.testing.base.ConfiguringTestBase):

	def test_registration(self):
		self.configure_string(ZCML_STRING)

		issuer = component.queryUtility(IIssuer, name="NTI")
		assert_that(issuer, is_not(none()))
		assert_that(issuer, has_property('name', 'NextThought'))
		assert_that(issuer, has_property('origin', 'http://www.nextthought.com'))
		assert_that(issuer, has_property('contact', 'contact@nextthought.com'))
		assert_that(issuer, has_property('org', 'http://www.nextthought.com'))

		manager = component.queryUtility(ITahrirBadgeManager)
		assert_that(manager, is_not(none()))
		assert_that(manager, has_property('autocommit', is_(False)))
		assert_that(manager, has_property('dburi', is_not(none())))
