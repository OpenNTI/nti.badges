#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Weak-references to Tahir objects. Like all weak references,
these are meant to be pickled with no external dependencies,
and when called, to be able to look up what they are missing.

.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope import component

from .interfaces import ITahrirBadgeManager
from .interfaces import IAssertion
from nti.wref.interfaces import ICachingWeakRef

@interface.implementer(ICachingWeakRef)
@component.adapter(IAssertion)
class AssertionWeakRef(object):

	_v_assertion = None

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
		except AttributeError:
			return NotImplemented

	def __hash__(self):
		return hash(self.__getstate__())

	def __call__(self, allow_cached=True):
		if allow_cached and self._v_assertion is not None:
			return self._v_assertion

		# NOTE: although we are saving the salt of the manager,
		# we are only actually checking the default manager.
		# This is currently fine because there is only one
		# such manager around but may change.
		manager = component.getUtility(ITahrirBadgeManager)

		assertion = manager.get_assertion(self._assertion_person_id, self._assertion_badge_id)
		if assertion is not None:
			self._v_assertion = assertion

		return assertion
