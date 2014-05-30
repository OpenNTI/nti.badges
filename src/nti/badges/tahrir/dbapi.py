#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import uuid
import hashlib
from datetime import datetime

from tahrir_api.model import Assertion
from tahrir_api.dbapi import autocommit
from tahrir_api.dbapi import TahrirDatabase

def salt_default():
	return unicode(uuid.uuid4())

class NTITahrirDatabase(TahrirDatabase):
	
	salt = salt_default()

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
			new_assertion.salt = self.salt
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