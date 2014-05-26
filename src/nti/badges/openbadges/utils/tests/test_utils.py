#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

import os

from nti.badges.openbadges import interfaces
from nti.badges.openbadges.utils import badge_from_source
from nti.badges.openbadges.utils import issuer_from_source
from nti.badges.openbadges.utils import assertion_from_source

from nti.testing.matchers import verifiably_provides

from nti.badges.tests import NTIBadgesTestCase

class TestUtils(NTIBadgesTestCase):

	def test_issuer_from_json(self):
		path = os.path.join(os.path.dirname(__file__), 'issuer.json')
		with open(path, "rb") as fp:
			issuer = issuer_from_source(fp)

		assert_that(issuer, is_not(none()))
		assert_that(issuer, verifiably_provides(interfaces.IIssuerOrganization))
		assert_that(issuer, has_property('name', is_('An Example Badge Issuer')))
		assert_that(issuer, has_property('image', is_("https://example.org/logo.png")))
		assert_that(issuer, has_property('url', is_("https://example.org")))
		assert_that(issuer, has_property('email', is_("steved@example.org")))
		assert_that(issuer, has_property('revocationList', is_("https://example.org/revoked.json")))

	def test_badge_from_json(self):
		path = os.path.join(os.path.dirname(__file__), 'badge.json')
		with open(path, "rb") as fp:
			badge = badge_from_source(fp)

		assert_that(badge, is_not(none()))
		assert_that(badge, verifiably_provides(interfaces.IBadgeClass))
		assert_that(badge, has_property('name', is_('Awesome Robotics Badge')))
		assert_that(badge, has_property('image', is_("https://example.org/robotics-badge.png")))
		assert_that(badge, has_property('description', is_("For doing awesome things with robots that people think is pretty great.")))
		assert_that(badge, has_property('criteria', is_("https://example.org/robotics-badge.html")))
		assert_that(badge, has_property('tags', is_(["robots", "awesome"])))
		assert_that(badge, has_property('issuer', is_("https://example.org/organization.json")))
		assert_that(badge, has_property('alignment'), has_length(1))
		alignment = badge.alignment[0]
		assert_that(alignment, has_property('name'), is_('CCSS.ELA-Literacy.RST.11-12.3'))
		assert_that(alignment, has_property('url'), is_('http://www.corestandards.org/ELA-Literacy/RST/11-12/3'))
		assert_that(alignment, has_property('description'), is_not(none()))

	def test_assertion_from_json(self):
		path = os.path.join(os.path.dirname(__file__), 'assertion.json')
		with open(path, "rb") as fp:
			assertion = assertion_from_source(fp)

		assert_that(assertion, is_not(none()))
		assert_that(assertion, verifiably_provides(interfaces.IBadgeAssertion))
		assert_that(assertion, has_property('uid', is_('f2c20')))
		assert_that(assertion, has_property('image', is_("https://example.org/beths-robot-badge.png")))
		assert_that(assertion, has_property('evidence', is_("https://example.org/beths-robot-work.html")))
		assert_that(assertion, has_property('issuedOn', is_not(none())))
		assert_that(assertion, has_property('badge', is_('https://example.org/robotics-badge.json')))
		assert_that(assertion, has_property('verify', is_not(none())))
		assert_that(assertion, has_property('recipient', is_not(none())))

		recipient = assertion.recipient
		assert_that(recipient, has_property('type', is_('email')))
		assert_that(recipient, has_property('hashed', is_(True)))
		assert_that(recipient, has_property('salt', is_('deadsea')))
		assert_that(recipient, has_property('identity', is_("sha256$c7ef86405ba71b85acd8e2e95166c4b111448089f2e1599f42fe1bba46e865c5")))

		verify = assertion.verify
		assert_that(verify, has_property('type', is_('hosted')))
		assert_that(verify, has_property('url', is_("https://example.org/beths-robotics-badge.json")))
