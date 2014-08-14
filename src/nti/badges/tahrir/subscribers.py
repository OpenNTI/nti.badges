#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from nti.dataserver.interfaces import IDataserverClosedEvent

from .manager import create_badge_manager

from .interfaces import ITahrirBadgeManager

@component.adapter(IDataserverClosedEvent)
def _closed_dataserver(event):
    db = create_badge_manager(dburi='sqlite://')
    component.getSiteManager().registerUtility(db, ITahrirBadgeManager)
