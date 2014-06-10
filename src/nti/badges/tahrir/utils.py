#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import threading
import transaction

def _after_transaction_end(success, manager, registry):
	try:
		manager.scoped_session.remove()
	except AttributeError:
		pass
	try:
		del registry.value
	except AttributeError:
		pass

class wrapper(object):

	def __init__(self, desc, subj):
		self.desc = desc
		self.subj = subj

	def __call__(self, *args, **kwargs):
		registry = self.desc.registry
		if not hasattr(registry, "value"):
			registry.value = True
			transaction.get().addAfterCommitHook(_after_transaction_end,
												 args=(self.subj, registry))
		return self.desc(self.subj, *args, **kwargs)

class autoclose(object):
	"""
	A decorator that remove scoped sessions
	"""

	registry = threading.local()

	def  __init__(self, func):
		self.func = func

	def __call__(self, *args, **kwargs):
		result = self.func(*args, **kwargs)
		return result
	
	def __get__(self, instance, owner):
		return wrapper(self, instance)


