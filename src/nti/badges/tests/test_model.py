#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import equal_to
from hamcrest import not_none
from hamcrest import has_entry
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

from nti.testing.matchers import verifiably_provides

import time

from nti.badges import model
from nti.badges import interfaces

from nti.externalization import internalization

from nti.externalization.externalization import toExternalObject

from nti.badges.tests import NTIBadgesTestCase

from nti.externalization.tests import assert_does_not_pickle


class TestNTIModel(NTIBadgesTestCase):

    def _issuer(self):
        result = model.NTIIssuer(name=u"FOSS@RIT",
                                 origin=u"http://foss.rit.edu/badges",
                                 organization=u"http://foss.rit.edu",
                                 email=u"foss@rit.edu")
        assert_does_not_pickle(result)
        return result

    def test_issuer(self):
        io = self._issuer()
        assert_that(io, verifiably_provides(interfaces.INTIIssuer))

        ext_obj = toExternalObject(io)
        assert_that(ext_obj, has_entry('Class', 'Issuer'))

        factory = internalization.find_factory_for(ext_obj)
        assert_that(factory, is_(not_none()))

        new_io = factory()
        internalization.update_from_external_object(new_io, ext_obj)
        assert_that(new_io, has_property('name', is_('FOSS@RIT')))
        assert_that(new_io, has_property('email', is_("foss@rit.edu")))
        assert_that(new_io,
                    has_property('origin', is_("http://foss.rit.edu/badges")))
        assert_that(new_io,
                    has_property('organization', is_("http://foss.rit.edu")))

        assert_that(io, equal_to(new_io))

    def _badge(self):
        issuer = self._issuer()
        result = model.NTIBadge(name=u"fossbox",
                                issuer=issuer,
                                description=u"Welcome to the FOSSBox. A member is you!",
                                image=u"http://foss.rit.edu/files/fossboxbadge.png",
                                criteria=u"http://foss.rit.edu/fossbox",
                                createdTime=time.time(),
                                tags=([u'fox', u'box']))
        assert_does_not_pickle(result)
        return result

    def test_badge(self):
        badge = self._badge()
        assert_that(badge, verifiably_provides(interfaces.INTIBadge))

        ext_obj = toExternalObject(badge)
        assert_that(ext_obj, has_entry('Class', 'Badge'))

        factory = internalization.find_factory_for(ext_obj)
        assert_that(factory, is_(not_none()))

        new_bg = factory()
        internalization.update_from_external_object(new_bg, ext_obj)
        assert_that(new_bg, has_property('name', is_('fossbox')))
        assert_that(new_bg, has_property('issuer', is_not(none())))
        assert_that(new_bg, has_property('createdTime', is_not(none())))
        assert_that(new_bg,
                    has_property('criteria', is_("http://foss.rit.edu/fossbox")))
        assert_that(new_bg,
                    has_property('image', is_("http://foss.rit.edu/files/fossboxbadge.png")))
        assert_that(new_bg,
                    has_property('description', is_(u"Welcome to the FOSSBox. A member is you!")))

        assert_that(badge, equal_to(new_bg))

    def _assertion(self):
        badge = self._badge()
        result = model.NTIAssertion(uid=u'breyAd5u',
                                    badge=badge,
                                    salt=u"2cf24dba",
                                    person=u'foo@example.org',
                                    recipient=u'ichigobleach',
                                    issuedOn=time.time())
        assert_does_not_pickle(result)
        return result

    def test_assertion(self):
        assertion = self._assertion()
        assert_that(assertion, verifiably_provides(interfaces.INTIAssertion))

        ext_obj = toExternalObject(assertion)
        assert_that(ext_obj, has_entry('Class', 'Assertion'))

        factory = internalization.find_factory_for(ext_obj)
        assert_that(factory, is_(not_none()))

        new_ast = factory()
        internalization.update_from_external_object(new_ast, ext_obj)
        assert_that(new_ast, has_property('uid', is_('breyAd5u')))
        assert_that(new_ast, has_property('badge', is_not(none())))
        assert_that(new_ast, has_property('salt', is_('2cf24dba')))
        assert_that(new_ast, has_property('issuedOn', is_not(none())))
        assert_that(new_ast, has_property('person', is_('foo@example.org')))
        assert_that(new_ast, has_property('recipient', is_('ichigobleach')))

        assert_that(assertion, equal_to(new_ast))

    def _person(self):
        result = model.NTIPerson(name=u'foo',
                                 email=u'foo@example.org',
                                 createdTime=time.time())
        assert_does_not_pickle(result)
        return result

    def test_person(self):
        person = self._person()
        assert_that(person, verifiably_provides(interfaces.INTIPerson))

        ext_obj = toExternalObject(person)
        assert_that(ext_obj, has_entry('Class', 'Person'))

        factory = internalization.find_factory_for(ext_obj)
        assert_that(factory, is_(not_none()))

        new_person = factory()
        internalization.update_from_external_object(new_person, ext_obj)
        assert_that(new_person, has_property('name', is_('foo')))
        assert_that(new_person, has_property('createdTime', is_not(none())))
        assert_that(new_person, has_property('email', is_('foo@example.org')))

        assert_that(person, equal_to(new_person))
