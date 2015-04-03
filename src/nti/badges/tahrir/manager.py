#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os
import ConfigParser

from zope import interface

from sqlalchemy import func
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from zope.sqlalchemy import ZopeTransactionExtension

from nti.common.property import Lazy

from tahrir_api.model import Badge
from tahrir_api.model import Issuer
from tahrir_api.model import Assertion
from tahrir_api.model import DeclarativeBase as tahrir_base

from .dbapi import NTITahrirDatabase

from .interfaces import IBadge
from .interfaces import IIssuer
from .interfaces import IPerson
from .interfaces import ITahrirBadgeManager

from ..interfaces import IEarnedBadge

@interface.implementer(ITahrirBadgeManager)
class TahrirBadgeManager(object):

	pool_size = 30
	max_overflow = 10
	pool_recycle = 300

	__metadata_created = False

	def __init__(self, dburi, twophase=False, autocommit=False, salt=None):
		self.salt = salt
		self.dburi = dburi
		self.twophase = twophase
		self.autocommit = autocommit

	@Lazy
	def defaultSQLite(self):
		return self.dburi.lower().startswith('sqlite:')

	@Lazy
	def engine(self):
		try:
			result = create_engine(self.dburi,
							   	   pool_size=self.pool_size,
							   	   max_overflow=self.max_overflow,
							   	   pool_recycle=self.pool_recycle)
		except TypeError:  # SQLite??
			result = create_engine(self.dburi)
		return result

	@Lazy
	def sessionmaker(self):
		if self.autocommit:
			result = sessionmaker(bind=self.engine,
							  	  twophase=self.twophase)
		else:
			result = sessionmaker(bind=self.engine,
								  autoflush=True,
							  	  twophase=self.twophase,
							  	  extension=ZopeTransactionExtension())
			
		return result

	@Lazy
	def scoped_session(self):
		result = scoped_session(self.sessionmaker)
		return result

	@Lazy
	def db(self):
		# make sure tables are created
		if not self.__metadata_created:
			metadata = getattr(tahrir_base, 'metadata')
			metadata.create_all(self.engine, checkfirst=True)
			self.__metadata_created = True

		# return db
		result = NTITahrirDatabase(session=self.scoped_session,
								   autocommit=self.autocommit,
							 	   salt=self.salt)
		return result

	# Badges

	def _badge_name(self, badge):
		badge = IBadge(badge)
		name = badge.name
		return name

	def add_badge(self, badge, issuer=None):
		database = self.db # get reference
		badge = IBadge(badge)
		issuer = self._get_issuer(issuer, database=database) if issuer is not None else None
		issuer_id = badge.issuer_id or issuer.id
		result = database.add_badge(name=badge.name,
								    image=badge.image,
								    desc=badge.description,
								    criteria=badge.criteria,
								    tags=badge.tags,
								    issuer_id=issuer_id,)
		return result

	def _get_badge(self, badge, database=None):
		database = self.db if database is None else database
		name = self._badge_name(badge)
		result = database.session.query(Badge) \
						 .filter(func.lower(Badge.name) == func.lower(name)).scalar()
		return result

	def badge_exists(self, badge):
		result = self._get_badge(badge)
		return True if result is not None else False

	def get_badge(self, badge):
		result = self._get_badge(badge)
		return result

	def get_all_badges(self):
		result = []
		for badge in self.db.get_all_badges():
			result.append(badge)
		return result

	def update_badge(self, badge, description=None, criteria=None, tags=None):
		database = self.db  # get reference
		stored = self._get_badge(badge, database=database)
		if stored is not None:
			source = IBadge(badge)
			tags = tags or source.tags or stored.tags
			criteria = criteria or source.criteria or stored.criteria
			description = description or source.description or stored.description
			database.update_badge(badge_id=stored.id,
								  tags=tags,
								  criteria=criteria,
								  description=description)
			return True
		return False

	def _get_person_badges(self, person, database=None):
		email, name = self._person_tuple(person)
		database = self.db if database is None else database
		assertions = database.get_assertions(email=email, nickname=name)
		result = [x.badge for x in assertions] if assertions else ()
		return result

	def get_person_badges(self, person):
		result = []
		for badge in self._get_person_badges(person):
			interface.alsoProvides(badge, IEarnedBadge)
			result.append(badge)
		return result

	def get_badge_by_id(self, badge_id):
		result = self.db.get_badge(badge_id)
		return result

	# Assertions

	def _get_assertion(self, person, badge, database=None):
		database = self.db if database is None else database
		badge = self._get_badge(badge, database=database)
		person = self._get_person(person, database=database)
		if badge and person:
			result = database.session.query(Assertion)\
				   			 .filter_by(person_id=person.id, badge_id=badge.id).scalar()
			if result is not None:
				result.salt = self.db.salt  # Save salt
				return result
		return None

	def get_assertion(self, person, badge):
		result = self._get_assertion(person, badge)
		return result

	def assertion_exists(self, person, badge):
		result = self._get_assertion(person, badge)
		return True if result is not None else False
	
	def update_assertion(self, uid, email=None, exported=True):
		result = self.db.update_assertion(uid, email=email, exported=exported)
		return True if result is not None else False
		
	def delete_assertion(self, person, badge):
		database = self.db  # get reference
		assertion = self._get_assertion(person, badge, database=database)
		if assertion is not None:
			database.session.delete(assertion)
			database.session.flush()
			return True
		return False
	remove_assertion = delete_assertion

	def _get_person_assertions(self, person, database=None):
		email, name = self._person_tuple(person)
		database = self.db if database is None else database
		assertions = database.get_assertions(email=email, nickname=name)
		return assertions if assertions else ()

	def get_person_assertions(self, person):
		result = []
		for assertion in self._get_person_assertions(person):
			assertion.salt = self.db.salt  # Save salt
			result.append(assertion)
		return result

	def add_assertion(self, person, badge, issued_on=None, exported=False):
		database = self.db  # get reference
		badge = self._get_badge(badge, database=database)
		person = self._get_person(person, database=database)
		if badge and person:
			return database.add_assertion(badge.id, person.email,
										  issued_on=issued_on,
										  exported=exported)
		return False

	def update_person(self, person, email=None, name=None, website=None, bio=None):
		database = self.db  # get reference
		stored = self._get_person(person, database=self.db)
		if stored is not None:
			source = IPerson(person)
			bio = bio or source.bio or stored.bio
			email = email or source.email or stored.email
			website = website or source.website or stored.website
			nickname = name or source.nickname or stored.nickname
			# set to none if they are the same
			email = None if email.lower() == stored.email.lower() else email
			nickname = None if nickname.lower() == stored.nickname.lower() else nickname
			# update
			database.update_person(person_id=stored.id,
								   bio=bio,
								   email=email,
								   website=website,
								   nickname=nickname)
			return True
		return False

	def _delete_person_assertions(self, person, database=None):
		result = 0
		database = self.db if database is None else database
		for ast in self._get_person_assertions(person, database):
			database.session.delete(ast)
			result += 1
		if result:
			database.session.flush()
		return result

	def delete_person_assertions(self, person):
		return self._delete_person_assertions(person)

	def get_assertion_by_id(self, assertion_id):
		result = self.db.get_assertion_by_id(assertion_id)
		return result

	# Persons

	def _person_tuple(self, person=None, name=None, email=None):
		person = IPerson(person, None)
		email = email or getattr(person, 'email', None)
		name = name or getattr(person, 'nickname', None)
		return (email, name)

	def _get_person(self, person=None, name=None, email=None, database=None):
		database = self.db if database is None else database
		email, name = self._person_tuple(person, name, email)
		result = database.get_person(person_email=email, nickname=name)
		return result

	def get_person(self, person=None, name=None, email=None):
		result = self._get_person(person, name, email)
		return result

	def add_person(self, person):
		person = IPerson(person)
		result = self.db.add_person(email=person.email,
									nickname=person.nickname,
									website=person.website,
									bio=person.bio)
		return result

	def person_exists(self, person=None, name=None):
		email, name, = self._person_tuple(person, name)
		result = self.db.person_exists(email=email, nickname=name)
		return result

	def delete_person(self, person):
		database = self.db  # get reference
		email, _ = self._person_tuple(person)
		self._delete_person_assertions(email, database=database)
		result = database.delete_person(email)
		return result

	def get_person_by_id(self, person_id):
		result = self.db.get_person(person_email=person_id, id=person_id)
		return result

	def get_all_persons(self):
		result = []
		for person in self.db.get_all_persons():
			result.append(person)
		return result
	
	# Issuers

	def get_all_issuers(self):
		result = []
		for issuer in self.db.get_all_issuers():
			result.append(issuer)
		return result
	
	def _issuer_tuple(self, issuer, origin=None):
		issuer = IIssuer(issuer)
		name = issuer.name
		origin = origin or issuer.origin
		return (name, origin)

	def _get_issuer(self, issuer, origin=None, database=None):
		database = self.db if database is None else database
		name, origin = self._issuer_tuple(issuer, origin)
		if database.issuer_exists(name=name, origin=origin):
			result = database.session.query(Issuer) \
						 	 .filter_by(name=name, origin=origin).one()
			return result
		return None

	def issuer_exists(self, issuer, origin=None):
		result = self._get_issuer(issuer, origin)
		return True if result is not None else False

	def get_issuer(self, issuer, origin=None):
		result = self._get_issuer(issuer, origin)
		return result

	def add_issuer(self, issuer):
		issuer = IIssuer(issuer)
		result = self.db.add_issuer(origin=issuer.origin,
									name=issuer.name,
									org=issuer.org,
									contact=issuer.contact)
		return result

	def get_issuer_by_id(self, issuer_id):
		result = self.db.get_issuer(issuer_id)
		return result
		
def create_badge_manager(dburi=None, twophase=False, salt=None,
						 autocommit=False, defaultSQLite=False, config=None):
	if defaultSQLite:
		data_dir = os.getenv('DATASERVER_DATA_DIR') or '/tmp'
		data_dir = os.path.expanduser(data_dir)
		data_file = os.path.join(data_dir, 'tahrir.db')
		dburi = "sqlite:///%s" % data_file
	elif config:  # if config file is specified
		config_name = os.path.expandvars(config)
		parser = ConfigParser.ConfigParser()
		parser.read([config_name])
		if parser.has_option('tahrir', 'salt'):
			salt = parser.get('tahrir', 'salt')
		if parser.has_option('tahrir', 'dburi'):
			dburi = parser.get('tahrir', 'dburi')
		if parser.has_option('tahrir', 'twophase'):
			twophase = parser.getboolean('tahrir', 'twophase')
		if parser.has_option('tahrir', 'autocommit'):
			autocommit = parser.getboolean('tahrir', 'autocommit')

	result = TahrirBadgeManager(dburi=dburi,
								salt=salt,
								twophase=twophase,
								autocommit=autocommit)
	return result

def create_issuer(name, origin, org, contact):
	result = Issuer()
	result.org = org
	result.name = name
	result.origin = origin
	result.contact = contact
	return result
