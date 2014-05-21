#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
Directives to be used in ZCML

$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import functools

from zope import interface
from zope.configuration import fields
from zope.component.zcml import utility

from . import interfaces
from .manager import create_badge_manager

class IRegisterTahrirDB(interface.Interface):
	"""
	The arguments needed for registering an Tahri db
	"""
	name = fields.TextLine(title="db name identifier (site)", required=False, default="")
	dburi = fields.TextLine(title="db dburi", required=False)
	twophase = fields.Bool(title='two phase commit protocol', required=False, default=False)
	defaultSQLite = fields.Bool(title='default to SQLLite', required=False, default=False)

def registerTahrirDB(_context, dburi=None, twophase=False, defaultSQLite=False,
					autocommit=False, name=u""):
	"""
	Register an db
	"""

	if not dburi and not defaultSQLite:
		raise ValueError("must specified valid database uri")

	factory = functools.partial(create_badge_manager,
								dburi=dburi,
								twophase=twophase,
								defaultSQLite=defaultSQLite,
								autocommit=autocommit)
	utility(_context, provides=interfaces.ITahrirBadgeManager,
			factory=factory, name=name)
