#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os
import uuid
import hashlib
from datetime import datetime

from zope import interface

from sqlalchemy import func
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from zope.sqlalchemy import ZopeTransactionExtension

from tahrir_api.model import Badge
from tahrir_api.model import Issuer
from tahrir_api.model import Assertion
from tahrir_api.dbapi import TahrirDatabase, autocommit
from tahrir_api.model import DeclarativeBase as tahrir_base

from nti.utils.property import Lazy

from . import interfaces
from .. import interfaces as badge_interfaces
from ..openbadges import interfaces as open_interfaces

def salt_default():
	return unicode(uuid.uuid4())

class NTITahrirDatabase(TahrirDatabase):
	
	salt = salt_default()

	def __init__(self, salt=None, *args, **kwargs):
		super(NTITahrirDatabase, self).__init__(*args, **kwargs)
		if salt is not None:
			self.salt = unicode(salt)

	def recipient(self, email):
		return unicode(hashlib.sha256(email + self.salt).hexdigest())

	@autocommit
	def add_assertion(self,
					  badge_id,
					  person_email,
					  issued_on=None,
					  issued_for=None):
		"""
		Add an assertion (award a badge) to the database

		:type badge_id: str
		:param badge_id: ID of the badge to be issued

		:type person_email: str
		:param person_email: Email of the Person to issue the badge to

		:type issued_on: DateTime
		:param issued_on: DateTime object holding the date the badge was issued
		on

		:type issued_for: str
		:param issued_for: An optional link back to the warranting event
		"""

		if issued_on is None:
			issued_on = datetime.utcnow()

		if self.person_exists(email=person_email) and \
		   self.badge_exists(badge_id):

			badge = self.get_badge(badge_id)
			person = self.get_person(person_email)
			old_rank = person.rank

			new_assertion = Assertion(badge_id=badge_id,
									  person_id=person.id,
									  issued_on=issued_on,
									  issued_for=issued_for,
									  recipient=self.recipient(person_email))
			self.session.add(new_assertion)
			self.session.flush()

			if self.notification_callback:
				self.notification_callback(
					topic='badge.award',
					msg=dict(
						badge=dict(
							name=badge.name,
							description=badge.description,
							image_url=badge.image,
							badge_id=badge_id,
						),
						user=dict(
							username=person.nickname,
							badges_user_id=person.id,
						)
					)
				)

			self._adjust_ranks(person, old_rank)
			return (person_email, badge_id)
		return False

@interface.implementer(interfaces.ITahrirBadgeManager)
class TahrirBadgeManager(object):

	def __init__(self, dburi, twophase=False, autocommit=True, salt=None):
		self.salt = salt
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
		result = NTITahrirDatabase(session=self.session, autocommit=self.autocommit,
								   salt=self.salt)
		self.session.configure(bind=self.engine)
		metadata = getattr(tahrir_base, 'metadata')
		metadata.create_all(self.engine, checkfirst=True)
		return result

	# DB operations

	def _person_tuple(self, person=None, email=None, name=None):
		if 	interfaces.IPerson.providedBy(person) or \
			badge_interfaces.INTIPerson.providedBy(person):
			pid = person.email  # Email is used as id
			email = email or person.email
			name = name or getattr(person, 'name', getattr(person, 'nickname', None))
		elif open_interfaces.IIdentityObject.providedBy(person):
			pid = person.identity
			name = name or person.identity
			email = email or person.identity
		else:
			pid = person
			name = name or person
			email = email or person
		return (pid, email, name)

	# Badges

	def _badge_name(self, badge):
		if	badge_interfaces.INTIBadge.providedBy(badge) or \
			open_interfaces.IBadgeClass.providedBy(badge) or \
			interfaces.IBadge.providedBy(badge):
			name = badge.name
		else:
			name = badge
		return name

	def add_badge(self, badge, issuer=None):
		badge = interfaces.IBadge(badge)
		issuer = self._get_issuer(issuer) if issuer is not None else None
		issuer_id = badge.issuer_id or issuer.id
		result = self.db.add_badge(name =badge.name,
								   image =badge.image,
								   desc=badge.description,
								   criteria=badge.criteria,
								   issuer_id=issuer_id,
								   tags=badge.tags)
		return result

	def _get_badge(self, badge):
		name = self._badge_name(badge)
		result = self.db.session.query(Badge) \
						.filter(func.lower(Badge.name) == func.lower(name)).all()
		return result[0] if result else None

	def get_badge(self, badge):
		result = self._get_badge(badge)
		return result
	
	def get_all_badges(self):
		result = []
		for badge in self.db.get_all_badges():
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
		return result

	def assertion_exists(self, person, badge):
		result = self._get_assertion(person, badge)
		return True if result is not None else False

	def delete_assertion(self, person, badge):
		assertion = self._get_assertion(person, badge)
		if assertion is None:
			self.db.session.delete(assertion)
			self.db.session.flush()
			return True
		return False
	remove_assertion = delete_assertion

	def _get_person_assertions(self, person):
		pid, _, _ = self._person_tuple(person)
		assertions = self.db.get_assertions_by_email(pid)
		return assertions if assertions else ()

	def get_person_assertions(self, person):
		result = []
		pid, _, _ = self._person_tuple(person)
		for assertion in self._get_person_assertions(pid):
			result.append(assertion)
		return result
	
	def add_assertion(self, person, badge, issued_on=None):
		badge = self._get_badge(badge)
		person = self._get_person(person)
		if badge and person:
			print('before', person.id, badge.id)
			return self.db.add_assertion(badge.id, person.email, issued_on)
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
		return result

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
			name = issuer.name
			origin = origin or issuer.origin
		elif open_interfaces.IIssuerOrganization.providedBy(issuer):
			name = issuer.name
			origin = origin or issuer.url
		elif interfaces.IIssuer.providedBy(issuer):
			name = issuer.name
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
		return result

	def add_issuer(self, issuer):
		issuer = interfaces.IIssuer(issuer)
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
