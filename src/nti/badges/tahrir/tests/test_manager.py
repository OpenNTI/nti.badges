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
from hamcrest import contains
from hamcrest import not_none
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

import os
import pickle
import shutil
import tempfile
from datetime import datetime
from six.moves import configparser

from zope import component

from zope.component import eventtesting

from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import ObjectCreatedEvent

from tahrir_api.model import Badge, Person, Issuer

from nti.wref.interfaces import IWeakRef

from nti.badges.tahrir import interfaces

from nti.badges.tahrir.manager import create_badge_manager

from nti.badges.tests import NTIBadgesTestCase


class TestTahrirBadgeManager(NTIBadgesTestCase):

    def test_registration(self):
        manager = component.queryUtility(interfaces.ITahrirBadgeManager)
        assert_that(manager, is_not(none()))

    def test_config(self):
        tmp_dir = tempfile.mkdtemp(dir="/tmp")
        try:
            config = configparser.RawConfigParser()
            config.add_section('tahrir')
            config.set('tahrir', 'dburi', 'mysql://Users:Users@myhost/Tahrir')
            config.set('tahrir', 'twophase', 'True')
            config.set('tahrir', 'salt', 'ichigo')

            config_file = os.path.join(tmp_dir, 'sample.cfg')
            with open(config_file, 'w') as configfile:
                config.write(configfile)

            manager = create_badge_manager(config=config_file)
            assert_that(manager, has_property('salt', 'ichigo'))
            assert_that(manager, has_property('twophase', is_(True)))
            assert_that(manager,
                        has_property('dburi', 'mysql://Users:Users@myhost/Tahrir'))
            assert_that(manager, has_property('defaultSQLite', is_(False)))
        finally:
            shutil.rmtree(tmp_dir, True)


class TestTahrirBadgeManagerOperation(NTIBadgesTestCase):

    def setUp(self):
        self.old = component.getUtility(interfaces.ITahrirBadgeManager)
        self.new = create_badge_manager(dburi='sqlite://')
        component.provideUtility(self.new)

    def tearDown(self):
        component.provideUtility(self.old)

    def test_fossboxbadge(self):
        manager = self.new
        assert_that(manager, is_not(none()))
        assert_that(manager, has_property('defaultSQLite', is_(True)))

        issuer_id = manager.db.add_issuer(u'http://foss.rit.edu/badges',
                                          u'FOSS@RIT',
                                          u'http://foss.rit.edu', u'foss@rit.edu')
        assert_that(issuer_id, is_not(none()))
        assert_that(manager.db.get_issuer(issuer_id), is_not(none()))

        badge_id = manager.db.add_badge(name=u'fossbox',
                                        image=u'http://foss.rit.edu/files/fossboxbadge.png',
                                        desc=u'Welcome to the FOSSBox. A member is you!',
                                        criteria=u'http://foss.rit.edu',
                                        issuer_id=issuer_id)
        assert_that(badge_id, is_not(none()))
        badge = manager.db.get_badge(badge_id)
        assert_that(badge, has_property('description',
                                        'Welcome to the FOSSBox. A member is you!'))
        assert_that(badge, has_property('criteria', 'http://foss.rit.edu'))
        assert_that(badge, has_property('tags', is_(none())))

        manager.db.update_badge(badge_id=badge_id,
                                description=u'Welcome to the FOSSBox',
                                criteria=u'http://foss.rit.org',
                                tags=u"fox, box")

        badge = manager.db.get_badge(badge_id)
        assert_that(badge,
                    has_property('description', 'Welcome to the FOSSBox'))
        assert_that(badge, has_property('criteria', 'http://foss.rit.org'))
        assert_that(badge, has_property('tags', 'fox, box'))

    def test_operations(self):
        manager = self.new

        issuer = Issuer()
        issuer.name = u'FOSS@RIT'
        issuer.origin = u'http://foss.rit.edu/badges'
        issuer.org = u'http://foss.rit.edu'
        issuer.contact = u'foss@rit.edu'
        issuer_id = manager.add_issuer(issuer)
        assert_that(issuer_id, is_not(none()))

        assert_that(manager.get_issuer(u'FOSS@RIT', u'http://foss.rit.edu/badges'),
                    is_not(none()))

        badge = Badge()
        badge.name = u'fossbox'
        badge.criteria = u'http://foss.rit.edu'
        badge.description = u'Welcome to the FOSSBox. A member is you!'
        badge.tags = u'fox,box,'
        badge.issuer_id = issuer_id
        badge.image = u'http://foss.rit.edu/files/fossboxbadge.png'
        badge_id = manager.add_badge(badge)
        assert_that(badge_id, is_not(badge))

        db_badge = manager.get_badge(u'fossbox')
        assert_that(db_badge, is_not(none()))

        person = Person()
        person.bio = u'I am foo'
        person.nickname = u'foo'
        person.email = u'foo@example.org'
        person.created_on = datetime.now()
        person.website = u'http://example.org/foo'

        pid = manager.add_person(person)
        assert_that(pid, is_('foo@example.org'))

        person = manager.get_person(pid)
        assert_that(person, has_property('bio', 'I am foo'))
        assert_that(person, has_property('website', 'http://example.org/foo'))

        update = manager.update_person(person, bio=u"I am foo!!!")
        assert_that(update, is_(True))

        person = manager.get_person(pid)
        assert_that(person, has_property('bio', 'I am foo!!!'))

        assert_that(manager.person_exists('foo@example.org'), is_(True))

        assert_that(manager.get_all_persons(), has_length(1))

        eventtesting.clearEvents()
        assert_that(manager.add_assertion('foo@example.org', 'fossbox'),
                    is_not(False))

        # Events
        # Adding the assertion should have fired typical object created
        # and added events
        events = eventtesting.getEvents()
        assert_that(events, has_length(2))
        assert_that(events,
                    contains(is_(ObjectCreatedEvent), is_(ObjectAddedEvent)))

        # WeakRefs
        # we can get a weak ref to this assertion, and then get the same object
        # back
        wref = IWeakRef(events[0].object)
        assert_that(wref, is_(wref))
        assert_that(hash(wref), is_(hash(wref)))
        assert_that(pickle.loads(pickle.dumps(wref)), is_(wref))

        assertion_from_wref = wref(allow_cached=False)
        assert_that(assertion_from_wref, is_(not_none()))
        assert_that(assertion_from_wref, is_(events[0].object))

        assertion = manager.get_assertion('foo@example.org', 'fossbox')
        assert_that(assertion, is_(not_none()))
        assert_that(assertion, is_(assertion_from_wref))
        assert_that(assertion, has_property("uid", is_(not_none())))
        assert_that(manager.assertion_exists('foo@example.org', 'fossbox'),
                    is_(True))
        assert_that(manager.db.assertion_exists('fossbox', 'foo@example.org'),
                    is_(True))

        uid = assertion.id
        manager.update_assertion(uid, exported=True)
        assertion = manager.get_assertion('foo@example.org', 'fossbox')
        assert_that(assertion, has_property('exported', is_(True)))

        badge = manager.get_badge('fossbox')
        assert_that(badge, is_not(none()))

        badges = manager.get_all_badges()
        assert_that(badges, has_length(1))

        badges = manager.get_person_badges('foo@example.org')
        assert_that(badges, has_length(1))

        assertions = manager.get_person_assertions('foo@example.org')
        assert_that(assertions, has_length(1))

        assert_that(manager.delete_person(pid), is_('foo@example.org'))

    def test_person_update(self):
        manager = self.new
        person = Person()
        person.bio = u'Shinigami'
        person.nickname = u'ichigo'
        person.email = u'ichigo@bleach.org'
        person.created_on = datetime.now()
        person.website = u'http://bleach.com/ichigo'

        pid = manager.add_person(person)
        assert_that(pid, is_('ichigo@bleach.org'))

        manager.update_person(person, email=u"ichigo@bleach.com")
        assert_that(manager.person_exists('ichigo@bleach.com'), is_(True))
        assert_that(manager.person_exists(name='ichigo'), is_(True))
