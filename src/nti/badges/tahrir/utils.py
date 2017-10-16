#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import threading
import transaction

logger = __import__('logging').getLogger(__name__)


def _after_transaction_end(success, manager, registry):
    __traceback_info__ = success, manager, registry
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
closer = Closer
