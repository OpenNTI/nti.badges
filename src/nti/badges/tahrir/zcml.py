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
from .manager import create_issuer
from .manager import create_badge_manager

class IRegisterTahrirDB(interface.Interface):
	"""
	The arguments needed for registering an Tahri db
	"""
	name = fields.TextLine(title="db name identifier (site)", required=False, default="")
	dburi = fields.TextLine(title="db dburi", required=False)
	salt = fields.TextLine(title='assertion salt', required=False)
	twophase = fields.Bool(title='two phase commit protocol', required=False, default=False)
	defaultSQLite = fields.Bool(title='default to SQLLite', required=False, default=False)
	config = fields.TextLine(title='path to a config file', required=False)

def registerTahrirDB(_context, dburi=None, twophase=False, salt=None,
					 defaultSQLite=False, autocommit=False, config=None, name=u""):
	"""
	Register an db
	"""

	if not dburi and not defaultSQLite and not config:
		raise ValueError("must specified valid database uri")

	factory = functools.partial(create_badge_manager,
								dburi=dburi,
								salt=salt,
								twophase=twophase,
								defaultSQLite=defaultSQLite,
								autocommit=autocommit,
								config=config)
	utility(_context, provides=interfaces.ITahrirBadgeManager,
			factory=factory, name=name)

class IRegisterTahrirIssuer(interface.Interface):
	"""
	The arguments needed for registering a Tahri issuer
	"""
	name = fields.TextLine(title="Issuer [unique] name")
	origin = fields.TextLine(title="Issuer origin [URL]")
	org = fields.TextLine(title="Issuer organization [URL]")
	contact = fields.TextLine(title="Issuer contact")
	id = fields.TextLine(title="Issuer zcml identifier", required=False, default='')

def registerTahrirIssuer(_context, name, origin, org, contact, id=u''):
	"""
	Register a Tahri issuer
	"""
	factory = functools.partial(create_issuer,
								name=name,
								origin=origin,
								org=org,
								contact=contact)
	utility(_context, provides=interfaces.IIssuer, factory=factory, name=id)

