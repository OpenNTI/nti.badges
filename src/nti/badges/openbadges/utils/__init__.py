#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six
import urllib
import simplejson
from collections import Mapping

from .. import model
from ..._compact import navstr

def _json_to_map(source, encoding=None):
    if hasattr(source, "read"):
        source = source.read()
    if isinstance(source, six.string_types):
        # check for a remote source
        if  source.startswith('http://') or \
            source.startswith('https://') or \
            source.startswith('file://') or \
            source.startswith('ftp://'):
            response = urllib.urlopen(source, source)
            source = response.read()
        # ready to parse
        source = simplejson.loads(source, encoding=encoding)
    assert isinstance(source, Mapping)
    return source

def issuerFromJSON(source, encoding=None):
    data = _json_to_map(source, encoding)
    result = model.IssuerObject()
    for field, func in (('name', str), ('image', navstr), ('url', navstr),
                        ('email', str), ('revocationList', navstr)):
        value = data.get(field)
        value = func(value) if value else None
        setattr(result, field, value)
    return result

def badgeFromJSON(source, encoding=None):
    data = _json_to_map(source, encoding)
    result = model.BadgeClass()

    # parse common single value fields
    for field, func in (('name', str), ('description', str), ('image', navstr),
                        ('criteria', navstr), ('issuer', navstr)):
        value = data.get(field)
        value = func(value) if value else None
        setattr(result, field, value)

    # alignment objects
    result.alignment = alignment = []
    for data in data.get('alignment', ()):
        ao = model.AlignmentObject()
        ao.name = data.get('name')
        ao.url = navstr(data.get('url', u''))
        ao.description = data.get('description')
        alignment.append(ao)

    return result
