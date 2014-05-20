#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from  collections import namedtuple

from zope import interface

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from zope.sqlalchemy import ZopeTransactionExtension

from tahrir_api.dbapi import TahrirDatabase
from tahrir_api.model import DeclarativeBase as tahrir_base

from nti.utils.property import Lazy

from . import interfaces

TahrirBadge = namedtuple("TahrirBadge", ["issuer", "data"])

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

	def delete_user(self, userid):
		return self.db.delete_person(userid)

	def get_all_badges(self):
		result = []
		for badge in self.db.get_all_badges():
			issuer = self.db.get_issuer(badge.issuer_id)
			obj = TahrirBadge(issuer.origin, badge)
			result.append(obj)
		return result

def create_badge_manager(dburi, twophase=False, autocommit=True):
	result = TahrirBadgeManager(dburi, twophase, autocommit)
	return result
