#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import six

logger = __import__('logging').getLogger(__name__)


def bytes_(s, encoding='utf-8', errors='strict'):
    """
    If ``s`` is an instance of ``text_type``, return
    ``s.encode(encoding, errors)``, otherwise return ``s``
    """
    if not isinstance(s, bytes) and s is not None:
        return s.encode(encoding, errors)
    return s


def text_(s, encoding='utf-8', err='strict'):
    """
    Return a string and unicode version of an object. 
    If the object is an byte sequence it's decoded first

    :param object s: The object to get an unicode representation of.
    :param str encoding: The encoding to be used if ``s`` is a byte sequence
    :param str err: The err handling scheme to be used if ``s`` is a byte sequence
    """
    s = s.decode(encoding, err) if isinstance(s, bytes) else s
    return six.text_type(s) if s is not None else None
str_ = text_  # alias
