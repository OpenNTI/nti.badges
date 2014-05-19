#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six

from zope import interface
from zope import component

from pyramid.threadlocal import get_current_request

from . import tahrir_interfaces

def get_possible_site_names(request=None, include_default=True):
	request = request or get_current_request()
	if not request:
		return () if not include_default else ('',)
	__traceback_info__ = request

	site_names = getattr(request, 'possible_site_names', ())
	if include_default:
		site_names += ('',)
	return site_names

def get_tahri_badgemanger(names=None, request=None):
	names = names.split() if isinstance(names, six.string_types) else names
	names = names or get_possible_site_names(request=request)
	for site in names:
		manager = component.queryUtility(tahrir_interfaces.ITahrirBadgeManager, name=site)
		if manager is not None:
			return manager
	return None

@interface.implementer(tahrir_interfaces.ITahrirBadgeManager)
class TahrirBadgeManager(object):

	def __init__(self, dburi):
		self.dburi = dburi
