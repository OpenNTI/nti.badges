#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component

from nti.badges.tahrir.interfaces import ITahrirBadgeManager

logger = __import__('logging').getLogger(__name__)


def get_tahrir_issuer_by_id(issuer_id):
    manager = component.getUtility(ITahrirBadgeManager)
    return manager.get_issuer_by_id(issuer_id)


def get_tahrir_badge_by_id(badge_id):
    manager = component.getUtility(ITahrirBadgeManager)
    return manager.get_badge_by_id(badge_id)


def get_tahrir_person_by_id(person_id):
    manager = component.getUtility(ITahrirBadgeManager)
    return manager.get_person_by_id(person_id)


def get_tahrir_assertion_by_id(assertion_id):
    manager = component.getUtility(ITahrirBadgeManager)
    return manager.get_assertion_by_id(assertion_id)
