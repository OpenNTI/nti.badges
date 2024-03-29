#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import equal_to
from hamcrest import not_none
from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_property

from nti.testing.matchers import verifiably_provides

import time
from datetime import datetime

from nti.externalization import internalization

from nti.externalization.externalization import toExternalObject

from nti.badges.openbadges import model
from nti.badges.openbadges import interfaces

from nti.externalization.tests import assert_does_not_pickle

from nti.badges.tests import NTIBadgesTestCase


class TestOpenBadges(NTIBadgesTestCase):

    def test_issuer_object(self):
        io = model.IssuerOrganization(name=u"foo",
                                      image=u"https://example.org/foo.png",
                                      url=u"http://example.org",
                                      email=u"foo@example.org",
                                      description=u"example issuer",
                                      revocationList=u"https://example.org/revoked.json")
        assert_that(io, verifiably_provides(interfaces.IIssuerOrganization))
        assert_does_not_pickle(io)

        ext_obj = toExternalObject(io)
        assert_that(ext_obj, has_entry('Class', 'Issuer'))
        assert_that(ext_obj, 
                    has_entry('MimeType', 'application/vnd.nextthought.openbadges.issuer'))

        factory = internalization.find_factory_for(ext_obj)
        assert_that(factory, is_(not_none()))

        new_io = factory()
        internalization.update_from_external_object(new_io, ext_obj)
        assert_that(new_io, has_property('name', is_('foo')))
        assert_that(new_io, has_property('url', is_("http://example.org")))
        assert_that(new_io, has_property('email', is_("foo@example.org")))
        assert_that(new_io, 
                    has_property('image', is_("https://example.org/foo.png")))
        assert_that(new_io, has_property('description', is_("example issuer")))
        assert_that(new_io, has_property('revocationList',
                                         is_("https://example.org/revoked.json")))

        assert_that(io, equal_to(new_io))

    def test_verification_object(self):
        vo = model.VerificationObject(type=u"hosted", url=u"http://foo.json")
        assert_that(vo, 
                    verifiably_provides(interfaces.IVerificationObject))
        assert_does_not_pickle(vo)

        ext_obj = toExternalObject(vo)
        assert_that(ext_obj, has_entry('Class', 'Verification'))
        assert_that(ext_obj, 
                    has_entry('MimeType', 'application/vnd.nextthought.openbadges.verificationobject'))

        factory = internalization.find_factory_for(ext_obj)
        assert_that(factory, is_(not_none()))

        new_vo = factory()
        internalization.update_from_external_object(new_vo, ext_obj)
        assert_that(new_vo, has_property('type', is_('hosted')))
        assert_that(new_vo, has_property('url', is_('http://foo.json')))

        assert_that(vo, equal_to(new_vo))

    def test_identity_object(self):
        io = model.IdentityObject(identity=u"my-identity", type=u"email",
                                  hashed=True, salt=u"xyz")
        assert_that(io, verifiably_provides(interfaces.IIdentityObject))
        assert_does_not_pickle(io)

        ext_obj = toExternalObject(io)
        assert_that(ext_obj, has_entry('Class', 'Identity'))
        assert_that(ext_obj, 
                    has_entry('MimeType', 'application/vnd.nextthought.openbadges.identityobject'))

        factory = internalization.find_factory_for(ext_obj)
        assert_that(factory, is_(not_none()))

        new_io = factory()
        internalization.update_from_external_object(new_io, ext_obj)
        assert_that(new_io, has_property('identity', is_('my-identity')))
        assert_that(new_io, has_property('type', is_('email')))
        assert_that(new_io, has_property('hashed', is_(True)))
        assert_that(new_io, has_property('salt', is_('xyz')))

        assert_that(io, equal_to(new_io))

    def test_alignment_object(self):
        ao = model.AlignmentObject(name=u"my-alignment", url=u"http://foo.xyz",
                                   description=u"foo")
        assert_that(ao, verifiably_provides(interfaces.IAlignmentObject))
        assert_does_not_pickle(ao)

        ext_obj = toExternalObject(ao)
        assert_that(ext_obj, has_entry('Class', 'Alignment'))
        assert_that(ext_obj, 
                    has_entry('MimeType', 'application/vnd.nextthought.openbadges.alignmentobject'))

        factory = internalization.find_factory_for(ext_obj)
        assert_that(factory, is_(not_none()))

        new_ao = factory()
        internalization.update_from_external_object(new_ao, ext_obj)
        assert_that(new_ao, has_property('name', is_('my-alignment')))
        assert_that(new_ao, has_property('url', is_('http://foo.xyz')))
        assert_that(new_ao, has_property('description', is_('foo')))

        assert_that(ao, equal_to(new_ao))

    def test_badge_class(self):

        ao1 = model.AlignmentObject(name=u"my-alignment-1", url=u"http://foo-1.xyz",
                                    description=u"foo-1")

        ao2 = model.AlignmentObject(name=u"my-alignment-2", url=u"http://foo-2.xyz",
                                    description=u"foo-2")

        bc = model.BadgeClass(name=u"my-badge",
                              description=u"super badge",
                              image=u"https://badge.png",
                              criteria=u"https://badge-criteria.com",
                              issuer=u"https://badge-issuer.com",
                              alignment=[ao1, ao2])
        assert_that(bc, verifiably_provides(interfaces.IBadgeClass))
        assert_does_not_pickle(bc)

        ext_obj = toExternalObject(bc)
        assert_that(ext_obj, has_entry('Class', 'Badge'))
        assert_that(ext_obj, 
                    has_entry('MimeType', 'application/vnd.nextthought.openbadges.badge'))

        factory = internalization.find_factory_for(ext_obj)
        assert_that(factory, is_(not_none()))

        new_bc = factory()
        internalization.update_from_external_object(new_bc, ext_obj)
        assert_that(new_bc, has_property('name', is_('my-badge')))
        assert_that(new_bc, has_property('image', is_('https://badge.png')))
        assert_that(new_bc, 
                    has_property('criteria', is_('https://badge-criteria.com')))
        assert_that(new_bc, 
                    has_property('issuer', is_('https://badge-issuer.com')))
        assert_that(new_bc, has_property('description', is_('super badge')))
        assert_that(new_bc, has_property('alignment', has_length(2)))
        assert_that(new_bc, has_property('alignment', is_([ao1, ao2])))

        assert_that(bc, equal_to(new_bc))

    def test_badge_assertion(self):
        now = datetime.fromtimestamp(int(time.time()))
        verify = model.VerificationObject(type=u"hosted", url=u"http://foo.json")
        recipient = model.IdentityObject(identity=u"my-identity", type=u"email",
                                         hashed=True, salt=u"xyz")
        ba = model.BadgeAssertion(uid=u"my-uid",
                                  recipient=recipient,
                                  verify=verify,
                                  badge=u"http://badge.json",
                                  issuedOn=now,
                                  image=u"http://foo.jpg",
                                  evidence=u"http://foo.com",
                                  expires=now)
        assert_that(ba, verifiably_provides(interfaces.IBadgeAssertion))
        assert_does_not_pickle(ba)

        ext_obj = toExternalObject(ba)
        assert_that(ext_obj, has_entry('Class', 'Assertion'))
        assert_that(ext_obj, 
                    has_entry('MimeType', 'application/vnd.nextthought.openbadges.assertion'))

        factory = internalization.find_factory_for(ext_obj)
        assert_that(factory, is_(not_none()))

        new_ba = factory()
        internalization.update_from_external_object(new_ba, ext_obj)
        assert_that(new_ba, has_property('uid', is_('my-uid')))
        assert_that(new_ba, has_property('verify', is_(equal_to(verify))))
        assert_that(new_ba, 
                    has_property('recipient', is_(equal_to(recipient))))
        assert_that(new_ba, has_property('issuedOn', is_(now)))
        assert_that(new_ba, has_property('image', is_('http://foo.jpg')))
        assert_that(new_ba, has_property('evidence', is_('http://foo.com')))
        assert_that(new_ba, has_property('expires', is_(now)))

        assert_that(ba, equal_to(new_ba))
