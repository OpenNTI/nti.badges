#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Weak-references to Tahir objects. Like all weak references,
these are meant to be pickled with no external dependencies,
and when called, to be able to look up what they are missing.

.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component
from zope import interface

from nti.badges.tahrir import get_tahrir_assertion_by_id

from nti.badges.tahrir.interfaces import IAssertion

from nti.property.property import alias

from nti.wref.interfaces import ICachingWeakRef

logger = __import__('logging').getLogger(__name__)


@component.adapter(IAssertion)
@interface.implementer(ICachingWeakRef)
class AssertionWeakRef(object):

    _v_assertion = None

    uid = alias('_assertion_id')

    def __init__(self, assertion):
        self._assertion_id = assertion.id
        self._assertion_salt = assertion.salt
        self._assertion_badge_id = assertion.badge_id
        self._assertion_person_id = assertion.person.email
        self._v_assertion = assertion

    def __getstate__(self):
        return (1,
                self._assertion_id,
                self._assertion_salt,
                self._assertion_badge_id,
                self._assertion_person_id)

    def __setstate__(self, state):
        assert isinstance(state, tuple)
        assert state[0] == 1
        self._assertion_id = state[1]
        self._assertion_salt = state[2]
        self._assertion_badge_id = state[3]
        self._assertion_person_id = state[4]

    def __eq__(self, other):
        try:
            return other is self or self.__getstate__() == other.__getstate__()
        except AttributeError:  # pragma: no cover
            return NotImplemented

    def __hash__(self):
        return hash(self.__getstate__())

    def __call__(self, allow_cached=False):
        # NOTE: Caching is disabled by default; there may be a ZODB
        # object cache interaction with SQLalchemy that leads to
        # ""DetachedInstanceError: Parent instance <Assertion at
        # 0x49250d50> is not bound to a Session; lazy load operation
        # of attribute 'badge' cannot proceed"
        # If so, it's possible this could be solved by the use of "long-lived"
        # sessions in the ZopeTransactionExtension, such that the session
        # stays bound to the thread/greenlet...although it may really
        # need to be bound to the connection, which we could also do with
        # an approriate session scope

        if allow_cached and self._v_assertion is not None:
            return self._v_assertion

        # NOTE: although we are saving the salt of the manager,
        # let's check all managers. Almost always there is only one
        # manager registered
        assertion = get_tahrir_assertion_by_id(self._assertion_id)
        if assertion is not None:
            self._v_assertion = assertion
        return assertion
