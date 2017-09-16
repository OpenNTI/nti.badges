#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import contains
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

import time
from datetime import datetime

from tahrir_api.model import Badge
from tahrir_api.model import Issuer
from tahrir_api.model import Person
from tahrir_api.model import Assertion

from nti.badges import interfaces as badge_interfaces

from nti.badges.model import NTIBadge
from nti.badges.model import NTIIssuer
from nti.badges.model import NTIPerson
from nti.badges.model import NTIAssertion

from nti.badges.openbadges import interfaces as open_interfaces

from nti.badges.openbadges.model import BadgeClass
from nti.badges.openbadges.model import IdentityObject
from nti.badges.openbadges.model import IssuerOrganization

from nti.badges.tahrir import interfaces as tahrir_interfaces

from nti.badges.tests import NTIBadgesTestCase


class TestAdapters(NTIBadgesTestCase):

    _time_now = time.time()
    _datetime_now = datetime.now()

    # Tahrir

    def _tahrir_person(self):
        person = Person()
        person.bio = u'I am foo'
        person.nickname = u'foo'
        person.email = u'foo@example.org'
        person.created_on = self._datetime_now
        return person

    def _tahrir_issuer(self):
        issuer = Issuer()
        issuer.name = u'FOSS@RIT'
        issuer.contact = u'foss@rit.ed'
        issuer.org = u'http://foss.rit.ed'
        issuer.created_on = self._datetime_now
        issuer.origin = u'http://foss.rit.edu/foss.json'
        return issuer

    def _tahrir_badge(self):
        badge = Badge()
        badge.tags = u'fox,box,'
        badge.name = u'fossbox'
        badge.issuer = self._tahrir_issuer()
        badge.created_on = self._datetime_now
        badge.criteria = u'http://foss.rit.ed'
        badge.image = u'http://foss.rit.edu/files/fossboxbadge.png'
        badge.description = u'Welcome to the FOSSBox. A member is you!'
        return badge

    def _tahrir_assertion(self):
        assertion = Assertion()
        assertion.id = u'fossbox -> foo@example.org'
        assertion.salt = u'a7425e'
        assertion.recipient = u'QxLUF1bgIAdX'
        assertion.issued_on = datetime.now()
        assertion.badge = self._tahrir_badge()
        assertion.person = self._tahrir_person()
        return assertion

    def test_tahrir_person_to_mozilla_identity_object(self):
        person = self._tahrir_person()
        iio = open_interfaces.IIdentityObject(person, None)
        assert_that(iio, is_not(none()))
        assert_that(iio, has_property('identity', 'foo@example.org'))

    def test_tahrir_issuer_to_mozilla_issuer(self):
        issuer = self._tahrir_issuer()
        nti = open_interfaces.IIssuerOrganization(issuer, None)
        assert_that(nti, is_not(none()))
        assert_that(nti, has_property('name', 'FOSS@RIT'))
        assert_that(nti, has_property('email', 'foss@rit.ed'))
        assert_that(nti, has_property('url', 'http://foss.rit.edu/foss.json'))
        assert_that(nti, has_property('description', 'http://foss.rit.ed'))

    def test_tahrir_issuer_to_mozilla_verification_object(self):
        issuer = self._tahrir_issuer()
        vo = open_interfaces.IVerificationObject(issuer, None)
        assert_that(vo, is_not(none()))
        assert_that(vo, has_property('type', 'hosted'))
        assert_that(vo, has_property('url', 'http://foss.rit.edu/foss.json'))

    def test_tahrir_badge_to_mozilla_badge(self):
        badge = self._tahrir_badge()
        bc = open_interfaces.IBadgeClass(badge, None)
        assert_that(bc, is_not(none()))
        assert_that(bc, has_property('name', 'fossbox'))
        assert_that(bc, has_property('tags', is_(('fox', 'box'))))
        assert_that(bc, has_property('criteria', 'http://foss.rit.ed'))
        assert_that(bc, 
                    has_property('image', 'http://foss.rit.edu/files/fossboxbadge.png'))
        assert_that(bc, 
                    has_property('description', 'Welcome to the FOSSBox. A member is you!'))
        assert_that(bc, 
                    has_property('issuer', 
                                 has_property('url', 'http://foss.rit.edu/foss.json')))

    def test_tahrir_assertion_to_mozilla_assertion(self):
        assertion = self._tahrir_assertion()
        ast = open_interfaces.IBadgeAssertion(assertion, None)
        assert_that(ast, 
                    has_property('uid', is_('fossbox -> foo@example.org')))
        assert_that(ast, 
                    has_property('badge', has_property('name', 'fossbox')))
        assert_that(ast, 
                    has_property('recipient', has_property('salt', 'a7425e')))
        assert_that(ast, 
                    has_property('recipient', has_property('identity', 'QxLUF1bgIAdX')))
        assert_that(ast, 
                    has_property('image', is_('http://foss.rit.edu/files/fossboxbadge.png')))
        assert_that(ast, 
                    has_property('verify', has_property('url', 'http://foss.rit.edu/foss.json')))

    def test_tahrir_person_to_ntiperson(self):
        person = self._tahrir_person()
        nti = badge_interfaces.INTIPerson(person, None)
        assert_that(nti, is_not(none()))
        assert_that(nti, has_property('name', 'foo'))
        assert_that(nti, has_property('email', 'foo@example.org'))
        assert_that(nti, has_property('createdTime', is_not(none())))

    def test_tahrir_issuer_to_ntiissuer(self):
        issuer = self._tahrir_issuer()
        nti = badge_interfaces.INTIIssuer(issuer, None)
        assert_that(nti, is_not(none()))
        assert_that(nti, has_property('name', 'FOSS@RIT'))
        assert_that(nti, has_property('email', 'foss@rit.ed'))
        assert_that(nti, has_property('createdTime', is_not(none())))
        assert_that(nti, has_property('organization', 'http://foss.rit.ed'))
        assert_that(nti, 
                    has_property('origin', 'http://foss.rit.edu/foss.json'))

    def test_tahrir_badge_to_ntibadge(self):
        badge = self._tahrir_badge()
        nti = badge_interfaces.INTIBadge(badge, None)
        assert_that(nti, is_not(none()))
        assert_that(nti, has_property('name', 'fossbox'))
        assert_that(nti, has_property('tags', is_(('fox', 'box'))))
        assert_that(nti, has_property('createdTime', is_not(none())))
        assert_that(nti, has_property('criteria', 'http://foss.rit.ed'))
        assert_that(nti,
                    has_property('image', 'http://foss.rit.edu/files/fossboxbadge.png'))
        assert_that(nti, 
                    has_property('description',
                                 'Welcome to the FOSSBox. A member is you!'))

    def test_tahrir_assertion_to_ntiassertion(self):
        assertion = self._tahrir_assertion()
        ast = badge_interfaces.INTIAssertion(assertion, None)
        assert_that(ast, has_property('salt', is_('a7425e')))
        assert_that(ast, has_property('badge', is_not(none())))
        assert_that(ast, has_property('issuedOn', is_not(none())))
        assert_that(ast, has_property('recipient', is_('QxLUF1bgIAdX')))
        assert_that(ast, 
                    has_property('person', has_property('email', 'foo@example.org')))

    # NTI

    def _ntiperson(self):
        person = NTIPerson()
        person.name = u'foo'
        person.bio = u'I am foo'
        person.email = u'foo@example.org'
        person.createdTime = self._time_now
        person.website = u'http://example.org/foo'
        return person

    def _ntiissuer(self):
        issuer = NTIIssuer()
        issuer.name = u'FOSS@RIT'
        issuer.email = u'foss@rit.ed'
        issuer.createdTime = self._time_now
        issuer.organization = u'http://foss.rit.ed'
        issuer.origin = u'http://foss.rit.edu/foss.json'
        return issuer

    def _ntibadge(self):
        result = NTIBadge(name=u"fossbox",
                          issuer=self._ntiissuer(),
                          description=u"Welcome to the FOSSBox. A member is you!",
                          image=u"http://foss.rit.edu/files/fossboxbadge.png",
                          criteria=u"http://foss.rit.edu/fossbox",
                          createdTime=self._time_now,
                          tags=([u'fox', u'box']))
        return result

    def _ntiassertion(self):
        result = NTIAssertion(uid=u'spadAsp4',
                              salt=u"2cf24dba",
                              badge=self._ntibadge(),
                              person=u'foo@example.org',
                              recipient=u"ichigobleach",
                              issuedOn=self._time_now)
        return result

    def test_ntiperson_to_tahrir_person(self):
        person = self._ntiperson()
        tah = tahrir_interfaces.IPerson(person, None)
        assert_that(tah, is_not(none()))
        assert_that(tah, has_property('nickname', 'foo'))
        assert_that(tah, has_property('bio', 'I am foo'))
        assert_that(tah, has_property('email', 'foo@example.org'))
        assert_that(tah, has_property('created_on', is_not(none())))
        assert_that(tah, has_property('website', 'http://example.org/foo'))

    def test_ntiissuer_to_mozilla_verification_object(self):
        issuer = self._ntiissuer()
        vo = open_interfaces.IVerificationObject(issuer, None)
        assert_that(vo, is_not(none()))
        assert_that(vo, has_property('type', 'hosted'))
        assert_that(vo, has_property('url', 'http://foss.rit.edu/foss.json'))

    def test_ntiissuer_to_mozilla_issuer(self):
        issuer = self._ntiissuer()
        io = open_interfaces.IIssuerOrganization(issuer, None)
        assert_that(io, is_not(none()))
        assert_that(io, has_property('name', 'FOSS@RIT'))
        assert_that(io, has_property('email', 'foss@rit.ed'))
        assert_that(io, has_property('url', 'http://foss.rit.edu/foss.json'))

    def test_ntibadge_to_tahrir_badge(self):
        badge = self._ntibadge()
        bc = tahrir_interfaces.IBadge(badge, None)
        assert_that(bc, is_not(none()))
        assert_that(bc, has_property('name', 'fossbox'))
        assert_that(bc, has_property('tags', 'fox,box'))
        assert_that(bc, has_property('issuer', is_(none())))
        assert_that(bc, 
                    has_property('criteria', 'http://foss.rit.edu/fossbox'))
        assert_that(bc, 
                    has_property('image', 'http://foss.rit.edu/files/fossboxbadge.png'))
        assert_that(bc, 
                    has_property('description',
                                 'Welcome to the FOSSBox. A member is you!'))

    def test_ntibadge_to_mozilla_badge(self):
        badge = self._ntibadge()
        bc = open_interfaces.IBadgeClass(badge, None)
        assert_that(bc, is_not(none()))
        assert_that(bc, has_property('name', 'fossbox'))
        assert_that(bc, has_property('tags', contains('fox', 'box')))
        assert_that(bc, 
                    has_property('issuer', 'http://foss.rit.edu/foss.json'))
        assert_that(bc, 
                    has_property('criteria', 'http://foss.rit.edu/fossbox'))
        assert_that(bc, 
                    has_property('image', 'http://foss.rit.edu/files/fossboxbadge.png'))
        assert_that(bc, 
                    has_property('description',
                                 'Welcome to the FOSSBox. A member is you!'))

    def test_ntiassertion_to_mozilla_assertion(self):
        assertion = self._ntiassertion()
        ast = open_interfaces.IBadgeAssertion(assertion, None)
        assert_that(ast, has_property('uid', is_('spadAsp4')))
        assert_that(ast, 
                    has_property('badge', has_property('name', 'fossbox')))
        assert_that(ast, 
                    has_property('recipient', has_property('salt', '2cf24dba')))
        assert_that(ast, 
                    has_property('recipient', has_property('identity', 'ichigobleach')))
        assert_that(ast, 
                    has_property('image', is_('http://foss.rit.edu/files/fossboxbadge.png')))
        assert_that(ast, 
                    has_property('verify', 
                                has_property('url', 'http://foss.rit.edu/foss.json')))

    # Mozilla

    def _open_issuer(self):
        issuer = IssuerOrganization(name=u"FOSS@RIT",
                                    image=u"http://foss.rit.edu/foss.png",
                                    url=u"http://foss.rit.edu/foss.json",
                                    email=u"foss@rit.edu",
                                    description=u"example issuer",
                                    revocationList=u"https://example.org/revoked.json")
        return issuer

    def _open_identityobject(self):
        io = IdentityObject(identity=u"foo@example.org", type=u"email",
                            hashed=False, salt=None)
        return io

    def _open_badge(self):
        result = BadgeClass(name=u"fossbox",
                            description=u"Welcome to the FOSSBox. A member is you!",
                            image=u"http://foss.rit.edu/files/fossboxbadge.png",
                            criteria=u"http://foss.rit.edu/fossbox",
                            issuer=u"http://foss.rit.edu/foss.json",
                            tags=(['fox', 'box']))
        return result

    def test_mozilla_io_to_tahrir_person(self):
        io = self._open_identityobject()
        tah = tahrir_interfaces.IPerson(io, None)
        assert_that(tah, is_not(none()))
        assert_that(tah, has_property('email', 'foo@example.org'))

    def test_mozilla_io_to_ntiperson(self):
        io = self._open_identityobject()
        nti = badge_interfaces.INTIPerson(io, None)
        assert_that(nti, is_not(none()))
        assert_that(nti, has_property('name', 'foo@example.org'))
        assert_that(nti, has_property('email', 'foo@example.org'))

    def test_mozilla_issuer_to_tahrir_issuer(self):
        issuer = self._open_issuer()
        tah = tahrir_interfaces.IIssuer(issuer, None)
        assert_that(tah, is_not(none()))
        assert_that(tah, has_property('name', 'FOSS@RIT'))
        assert_that(tah, has_property('contact', 'foss@rit.edu'))
        assert_that(tah, has_property('org', 'http://foss.rit.edu/foss.json'))
        assert_that(tah, has_property('image', 'http://foss.rit.edu/foss.png'))
        assert_that(tah, 
                    has_property('origin', 'http://foss.rit.edu/foss.json'))

    def test_mozilla_issuer_to_ntiissuer(self):
        issuer = self._open_issuer()
        nti = badge_interfaces.INTIIssuer(issuer, None)
        assert_that(nti, is_not(none()))
        assert_that(nti, has_property('name', 'FOSS@RIT'))
        assert_that(nti, has_property('email', 'foss@rit.edu'))
        assert_that(nti, 
                    has_property('origin', 'http://foss.rit.edu/foss.json'))
        assert_that(nti, 
                    has_property('organization',
                                 'http://foss.rit.edu/foss.json'))

    def test_mozilla_badge_to_ntibadge(self):
        badge = self._open_badge()
        nti = badge_interfaces.INTIBadge(badge, None)
        assert_that(nti, is_not(none()))
        assert_that(nti, has_property('name', 'fossbox'))
        assert_that(nti, has_property('issuer', is_(none())))
        assert_that(nti, has_property('tags', contains('fox', 'box')))
        assert_that(nti,
                    has_property('criteria', 'http://foss.rit.edu/fossbox'))
        assert_that(nti, 
                    has_property('image', 'http://foss.rit.edu/files/fossboxbadge.png'))
        assert_that(nti, 
                    has_property('description',
                                 'Welcome to the FOSSBox. A member is you!'))

    def test_mozilla_badge_to_tahrir_badge(self):
        badge = self._open_badge()
        nti = tahrir_interfaces.IBadge(badge, None)
        assert_that(nti, is_not(none()))
        assert_that(nti, has_property('name', 'fossbox'))
        assert_that(nti, has_property('issuer', is_(none())))
        assert_that(nti, has_property('tags', is_('fox,box')))
        assert_that(nti,
                    has_property('criteria', 'http://foss.rit.edu/fossbox'))
        assert_that(nti, 
                    has_property('image', 'http://foss.rit.edu/files/fossboxbadge.png'))
        assert_that(nti, 
                    has_property('description',
                                 'Welcome to the FOSSBox. A member is you!'))

    # misc

    def test_string_to_tahrir_issuer(self):
        issuer = tahrir_interfaces.IIssuer('FOSS@RIT', None)
        assert_that(issuer, is_not(none()))
        assert_that(issuer, has_property('name', 'FOSS@RIT'))

    def test_collection_to_tahrir_issuer(self):
        data = ('FOSS@RIT', 'http://foss.rit.edu/foss.json')
        issuer = tahrir_interfaces.IIssuer(data, None)
        assert_that(issuer, is_not(none()))
        assert_that(issuer, has_property('name', 'FOSS@RIT'))
        assert_that(issuer,
                    has_property('origin', 'http://foss.rit.edu/foss.json'))

        issuer = tahrir_interfaces.IIssuer(list(data), None)
        assert_that(issuer, is_not(none()))
        assert_that(issuer, has_property('name', 'FOSS@RIT'))
        assert_that(issuer,
                    has_property('origin', 'http://foss.rit.edu/foss.json'))
