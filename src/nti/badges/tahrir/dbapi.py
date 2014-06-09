#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import base64
import hashlib
from datetime import datetime

from sqlalchemy import func, exists, and_

from tahrir_api.model import Badge
from tahrir_api.model import Person
from tahrir_api.model import Issuer
from tahrir_api.model import Assertion
from tahrir_api.dbapi import autocommit
from tahrir_api.dbapi import TahrirDatabase

from zope import lifecycleevent

def salt_default():
	return u'23597b11-857a-447f-8129-66b5397b0c7f'

class NTITahrirDatabase(TahrirDatabase):

	def __init__(self, salt=None, *args, **kwargs):
		super(NTITahrirDatabase, self).__init__(*args, **kwargs)
		self.salt = salt or salt_default()

	def assertion_id(self, person_id, badge_id):
		result = "%s -> %r" % (badge_id, person_id)
		result = base64.urlsafe_b64encode(result)
		return unicode(result)

	def recipient(self, email):
		hexdigest = unicode(hashlib.sha256(email + self.salt).hexdigest())
		return u"sha256$" + hexdigest

	# issuers

	def issuer_exists(self, origin, name):
		query = self.session.query(
						exists().where(
							and_(func.lower(Issuer.origin) == func.lower(origin),
								 func.lower(Issuer.name) == func.lower(name))))
		return query.scalar()

	def get_issuer(self, issuer_id):
		query = self.session.query(Issuer).filter_by(id=issuer_id)
		result = query.scalar()
		return result

	# badges

	def badge_exists(self, badge_id):
		result = self.session.query(exists().where(
							func.lower(Badge.id) == func.lower(badge_id))).scalar()
		return result

	def update_badge(self, badge_id, description, criteria, tags):
		result = self.session.query(Badge).filter_by(id=badge_id).\
   								update({"description":description,
										"criteria":criteria,
										"tags":tags})
		return result

	# persons

	def person_exists(self, email=None, id=None, nickname=None):
		result = False
		if email:
			result = self.session.query(exists().where(
							func.lower(Person.email) == func.lower(email))).scalar()
		elif id:
			result = self.session.query(exists().where(Person.id == id)).scalar()
		elif nickname:
			result = self.session.query(exists().where(
							func.lower(Person.nickname) == func.lower(nickname))).scalar()
		return result

	# assertion

	def assertion_exists(self, badge_id, email):
		person = self.get_person(email)
		if not person:
			return False

		result = self.session.query(exists().where(
							and_(func.lower(Assertion.person_id) == func.lower(person.id),
								 func.lower(Assertion.badge_id) == func.lower(badge_id)))).scalar()
							
		return result

	@autocommit
	def add_assertion(self,
					  badge_id,
					  person_email,
					  issued_on=None,
					  issued_for=None):
		"""
		Add an assertion (award a badge) to the database.

		Lifecycle events are fired for the creation and addition
		of the :class:`tahrir_api.model.Assertion` object. For the addition
		event, the name and parent are synthetic and correspond to the
		id and the person.

		.. note:: This is currently not assured to be symmetrical; there is no
			guarantee that any events are fired when the assertion is removed,
			or the badge or person is removed.

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

		if (not self.person_exists(email=person_email)
			or not self.badge_exists(badge_id)):
			return False # TODO: Should probably be an empty tuple

		if issued_on is None:
			issued_on = datetime.utcnow()

		badge = self.get_badge(badge_id)
		person = self.get_person(person_email)
		old_rank = person.rank

		aid = self.assertion_id(person.id, badge_id)
		new_assertion = Assertion(id=aid,
								  badge_id=badge_id,
								  person_id=person.id,
								  issued_on=issued_on,
								  issued_for=issued_for,
								  recipient=self.recipient(person_email))
		new_assertion.salt = self.salt

		lifecycleevent.created(new_assertion)

		self.session.add(new_assertion)
		self.session.flush()

		lifecycleevent.added(new_assertion, person, aid)

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
