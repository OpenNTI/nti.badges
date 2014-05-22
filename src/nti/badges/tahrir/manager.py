#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os

from zope import interface

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from zope.sqlalchemy import ZopeTransactionExtension

from tahrir_api.dbapi import TahrirDatabase
from tahrir_api.model import DeclarativeBase as tahrir_base

from nti.utils.property import Lazy

from . import interfaces
from .. import interfaces as badge_interfaces
from .model import TahrirIssuer, TahrirBadge, TahrirAssertion

class NTITahrirDatabase(TahrirDatabase):
	pass

@interface.implementer(interfaces.ITahrirBadgeManager)
class TahrirBadgeManager(object):

	def __init__(self, dburi, twophase=False, autocommit=True):
		self.dburi = dburi
		self.twophase = twophase
		self.autocommit = autocommit

	@Lazy
	def engine(self):
		result = create_engine(self.dburi)
		return result

	@Lazy
	def sessionmaker(self):
		result = sessionmaker(bind=self.engine,
							  twophase=self.twophase,
							  extension=ZopeTransactionExtension())
		return result

	@Lazy
	def session(self):
		result = scoped_session(self.sessionmaker)
		return result

	@Lazy
	def db(self):
		result = NTITahrirDatabase(session=self.session, autocommit=self.autocommit)
		self.session.configure(bind=self.engine)
		metadata = getattr(tahrir_base, 'metadata')
		metadata.create_all(self.engine, checkfirst=True)
		return result

	# DB operations

	def delete_user(self, userid):
		return self.db.delete_person(userid)

	def _tahrir_issuer(self, issuer):
		result = TahrirIssuer(uri=issuer.name, org=issuer.org)
		return result

	def _tahrir_badge(self, badge):
		issuer = self.db.get_issuer(badge.issuer_id)
		issuer = self._tahrir_issuer(issuer)
		result = TahrirBadge(issuer=issuer, badge=badge)
		return result

	def get_all_badges(self):
		result = []
		for badge in self.db.get_all_badges():
			badge = self._tahrir_badge(badge)
			result.append(badge)
		return result

	def _user_assertions_badges(self, userid):
		for ast in self.db.get_assertions_by_email(userid):
			yield ast, ast.badge
			
	def get_user_badges(self, userid):
		result = []
		for _, badge in self._user_assertions_badges(userid):
			badge = self._tahrir_badge(badge)
			interface.alsoProvides(badge, badge_interfaces.IEarnedBadge)
			result.append(badge)
		return result

	def get_user_assertions(self, userid):
		result = []
		for ast, badge in self._user_assertions_badges(userid):
			badge = self._tahrir_badge(badge)
			interface.alsoProvides(badge, badge_interfaces.IEarnedBadge)
			assertion = TahrirAssertion(badge=badge,
										recipient=userid,
										issueOn=ast.issued_on)
			result.append(assertion)
		return result

def create_badge_manager(dburi=None, twophase=False, defaultSQLite=False, autocommit=False):
	if defaultSQLite:
		data_dir = os.getenv('DATASERVER_DATA_DIR') or '/tmp'
		data_dir = os.path.expanduser(data_dir)
		data_file = os.path.join(data_dir, 'tahrir.db')
		dburi = "sqlite:///%s" % data_file
	result = TahrirBadgeManager(dburi, twophase, autocommit)
	return result
