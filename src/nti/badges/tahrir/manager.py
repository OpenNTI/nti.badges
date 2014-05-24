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

from sqlalchemy import func
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from zope.sqlalchemy import ZopeTransactionExtension

from tahrir_api.model import Badge
from tahrir_api.model import Issuer
from tahrir_api.model import Assertion
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
		result = badge_interfaces.INTIBadge(badge, None)
		return result

	def _person_tuple(self, person=None, email=None, name=None):
		if 	badge_interfaces.INTIPerson.providedBy(person) or \
			interfaces.IPerson.providedBy(person):
			pid = person.email  # Email is used as id
			email = email or person.email
			name = name or getattr(person, 'name', getattr(person, 'nickname', None))
		else:
			pid = person
			name = name or person
			email = email or person
		return (pid, email, name)

	# Badges

	def _badge_name(self, badge):
		if	badge_interfaces.INTIBadge.providedBy(badge) or \
			interfaces.IBadge.providedBy(badge):
			name = badge.name
		else:
			name = badge
		return name

	def add_badge(self, badge):
		badge = interfaces.IBadge(badge)
		result = self.db.add_badge(name =badge.name,
								   image =badge.image,
								   desc=badge.description,
								   criteria=badge.criteria,
								   issuer_id=badge.issuer_id,
								   tags=badge.tags)
		return result

	def _get_badge(self, badge):
		name = self._badge_name(badge)
		result = self.db.session.query(Badge) \
						.filter(func.lower(Badge.name) == func.lower(name)).all()
		return result[0] if result else None

	def get_badge(self, badge):
		result = self._get_badge(badge)
		return self._nti_badge(result)
	
	def get_all_badges(self):
		result = []
		for badge in self.db.get_all_badges():
			badge = self._nti_badge(badge)
			result.append(badge)
		return result

	def _get_person_badges(self, person):
		pid, _, _ = self._person_tuple(person)
		assertions = self.db.get_assertions_by_email(pid)
		result = [x.badge for x in assertions] if assertions else ()
		return result

	def get_person_badges(self, person):
		result = []
		for badge in self._get_person_badges(person):
			badge = self._nti_badge(badge)
			interface.alsoProvides(badge, badge_interfaces.IEarnedBadge)
			result.append(badge)
		return result

	# Assertions

	def _get_assertion(self, person, badge):
		badge = self._get_badge(badge)
		person = self._get_person(person)
		if badge and person:
			result = self.db.session.query(Assertion)\
				   		 .filter_by(person_id=person.id, badge_id=badge.id).all()
			return result[0] if result else None
		return None

	def get_assertion(self, person, badge):
		result = self._get_assertion(person, badge)
		return badge_interfaces.INTIAssertion(result, None)

	def delete_assertion(self, person, badge):
		assertion = self._get_assertion(person, badge)
		if assertion is None:
			self.db.session.delete(assertion)
			self.db.session.flush()
			return True
		return False

	def _get_person_assertions(self, person):
		pid, _, _ = self._person_tuple(person)
		assertions = self.db.get_assertions_by_email(pid)
		return assertions if assertions else ()

	def get_person_assertions(self, person):
		result = []
		pid, _, _ = self._person_tuple(person)
		for ast in self._get_person_assertions(pid):
			assertion = badge_interfaces.INTIAssertion(ast)
			assertion.recipient = pid
			result.append(assertion)
		return result
	
	def add_assertion(self, person, badge):
		badge = self._get_badge(badge)
		person = self._get_person(person)
		if badge and person:
			return self.db.add_assertion(badge.id, person.email, None)
		return False

	def delete_person_assertions(self, person):
		result = 0
		for ast in self._get_person_assertions(person):
			self.db.session.delete(ast)
			result += 1
		if result:
			self.db.session.flush()
		return result

	# Persons
	
	def _get_person(self, person=None, email=None, name=None):
		pid, email, name = self._person_tuple(person, email, name)
		result = self.db.get_person(person_email=email, id=pid, nickname=name)
		return result

	def get_person(self, person=None, email=None, name=None):
		result = self._get_person(person, email, name)
		return badge_interfaces.INTIPerson(result, None)

	def add_person(self, person):
		person = interfaces.IPerson(person)
		result = self.db.add_person(email=person.email,
									nickname=person.nickname,
									website=person.website,
									bio=person.bio)
		return result

	def person_exists(self, person=None, email=None, name=None):
		pid, email, name, = self._person_tuple(person, email, name)
		result = self.db.person_exists(email=email, id=pid, nickname=name)
		return result

	def delete_person(self, person):
		pid, _, _ = self._person_tuple(person)
		self.delete_person_assertions(pid)
		return self.db.delete_person(pid)

	# Issuers

	def _issuer_tuple(self, issuer, origin=None):
		if badge_interfaces.INTIIssuer.providedBy(issuer):
			name = issuer.uri
			origin = origin or issuer.origin
		else:
			name = issuer
		return (name, origin)
	
	def _get_issuer(self, issuer, origin=None):
		name, origin = self._issuer_tuple(issuer, origin)
		if self.db.issuer_exists(name=name, origin=origin):
			result = self.db.session.query(Issuer) \
						 	.filter_by(name=name, origin=origin).one()
			return result
		return None

	def get_issuer(self, issuer, origin=None):
		result = self._get_issuer(issuer, origin)
		return badge_interfaces.INTIIssuer(result, None)

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
