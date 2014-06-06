#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from .tahrir import interfaces as tahrir_interfaces

def get_tahrir_issuer_by_id(issuer_id):
    for _, manager in component.getUtilitiesFor(tahrir_interfaces.ITahrirBadgeManager):
        result = manager.get_issuer_by_id(issuer_id)
        if result is not None:
            return result
    return None

def get_tahrir_badge_by_id(badge_id):
    for _, manager in component.getUtilitiesFor(tahrir_interfaces.ITahrirBadgeManager):
        result = manager.get_badge_by_id(badge_id)
        if result is not None:
            return result
    return None

def get_tahrir_person_by_id(person_id):
    for _, manager in component.getUtilitiesFor(tahrir_interfaces.ITahrirBadgeManager):
        result = manager.get_person_by_id(person_id)
        if result is not None:
            return result
    return None
