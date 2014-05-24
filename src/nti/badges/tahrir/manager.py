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

from sqlalchemy import or_
from sqlalchemy import func
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from zope.sqlalchemy import ZopeTransactionExtension

from tahrir_api.model import Badge
from tahrir_api.model import Issuer
from tahrir_api.dbapi import TahrirDatabase
from tahrir_api.model import DeclarativeBase as tahrir_base

from nti.utils.property import Lazy

from . import interfaces
from .. import interfaces as badge_interfaces

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

	def _nti_issuer(self, issuer):
		result = badge_interfaces.INTIIssuer(issuer)
		return result

	def _nti_badge(self, badge):
		result = badge_interfaces.INTIBadge(badge)
		return result

	def _person_assertions_badges(self, pid):
		assertions = self.db.get_assertions_by_email(pid)
		if assertions:
			for ast in self.db.get_assertions_by_email(pid):
				yield ast, ast.badge

	def _person_tuple(self, person, email=None, name=None):
		if badge_interfaces.INTIPerson.providedBy(person):
			pid = person.name
			name = name or person.name
			email = email or person.email
		else:
			pid = person
		return (pid, name, email)

	# Badges

	def _badge_tuple(self, badge):
		if badge_interfaces.INTIBadge.providedBy(badge):
			iden, name = badge.id, badge.name,
		else:
			iden, name = badge, badge
		return (iden, name)

	def get_badge(self, badge):
		"""
		return the specifed badge
		"""
		iden, name = self._badge_tuple(badge)
		result = self.db.session.query(Badge) \
						.filter(or_(func.lower(Badge.name) == func.lower(name),
									func.lower(Badge.id) == func.lower(iden))).all()
		return result[0] if result else None
	
	def get_all_badges(self):
		result = []
		for badge in self.db.get_all_badges():
			badge = self._nti_badge(badge)
			result.append(badge)
		return result

	def get_person_badges(self, person):
		result = []
		pid, _, _ = self._person_tuple(person)
		for _, badge in self._person_assertions_badges(pid):
			badge = self._nti_badge(badge)
			interface.alsoProvides(badge, badge_interfaces.IEarnedBadge)
			result.append(badge)
		return result

	# Assertions

	def get_person_assertions(self, pid):
		result = []
		for ast, _ in self._person_assertions_badges(pid):
			assertion = badge_interfaces.INTIAssertion(ast)
			result.append(assertion)
			# do we want to change the recipient?
			if assertion.recipient != pid:
				assertion.recipient = pid
		return result

	# Persons
	
	def add_person(self, person):
		person = interfaces.IPerson(person)
		result = self.db.add_person(email=person.email,
									nickname=person.nickname,
									website=person.website,
									bio=person.bio)
		return result

	def person_exists(self, person=None, email=None, name=None):
		pid, email, name = self._person_tuple(person, email, name)
		result = self.db.person_exists(email=email, id=pid, nickname=name)
		return result

	def get_person(self, person=None, email=None, name=None):
		pid, email, name = self._person_tuple(person, email, name)
		result = self.db.get_person(person_email=email, id=pid, nickname=name)
		return badge_interfaces.INTIPerson(result, None)

	def delete_person(self, person):
		pid, _, _ = self._person_tuple(person)
		return self.db.delete_person(pid)

	# Issuers

	def _issuer_tuple(self, issuer, origin=None):
		if badge_interfaces.INTIIssuer.providedBy(issuer):
			name = issuer.uri
			origin = origin or issuer.origin
		else:
			name = issuer
		return (name, origin)
	
	def get_issuer(self, issuer, origin=None):
		name, origin = self._issuer_tuple(issuer, origin)
		if self.db.issuer_exists(name=name, origin=origin):
			result = self.db.session.query(Issuer) \
						 	.filter_by(name=name, origin=origin).one()
			return result
		return None

	def add_issuer(self, issuer):
		result = self.db.add_issuer(origin=issuer.origin,
									name=issuer.name,
									org=issuer.org,
									contact=issuer.contact)
		return result

def create_badge_manager(dburi=None, twophase=False, defaultSQLite=False, autocommit=False):
	if defaultSQLite:
		data_dir = os.getenv('DATASERVER_DATA_DIR') or '/tmp'
		data_dir = os.path.expanduser(data_dir)
		data_file = os.path.join(data_dir, 'tahrir.db')
		dburi = "sqlite:///%s" % data_file
	result = TahrirBadgeManager(dburi, twophase, autocommit)
	return result

def create_issuer(name, origin, org, contact):
	result = Issuer()
	result.org = org
	result.name = name
	result.origin = origin
	result.contact = contact
	return result
