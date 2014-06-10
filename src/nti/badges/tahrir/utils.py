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

def Closer(clazz):

	def __init__(self, *args, **kwargs):
		self.registry = threading.local()
		self.wrapped = clazz(*args, **kwargs)

	def __getattr__(self, attrname):
		registry = self.registry
		if not hasattr(registry, "value"):
			registry.value = True
			transaction.get().addAfterCommitHook(_after_transaction_end,
												 args=(self.wrapped, registry))
		return getattr(self.wrapped, attrname)


