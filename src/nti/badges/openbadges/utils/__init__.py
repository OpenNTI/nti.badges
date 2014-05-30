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
from datetime import datetime
from collections import Mapping
from dateutil.parser import parse

import simplejson

from itsdangerous import BadSignature
from itsdangerous import JSONWebSignatureSerializer

from nti.utils.maps import CaseInsensitiveDict

from .. import model
from .. import navstr

DEFAULT_SECRET = u'!f^#GQ5md{)Rf&Z'

def _datetime(s):
    if isinstance(s, basestring):
        result = parse(s)
    else:
        result = datetime.fromtimestamp(float(s))
    return result

def _unicode(s):
    s.decode("utf-8") if isinstance(s, bytes) else s
    return unicode(s) if s is not None else None

def load_data(source, encoding='UTF-8', secret=DEFAULT_SECRET):
    try:
        result = simplejson.loads(source, encoding=encoding)
    except simplejson.JSONDecodeError:
        jws = JSONWebSignatureSerializer(secret)
        try:
            result = jws.loads(source)
        except BadSignature:
            raise ValueError("Bad source signature")
        except:
            raise ValueError("Cannot load source data")
    return result

def process_json_source(source, **kwargs):
    if hasattr(source, "read"):
        source = source.read()
    if isinstance(source, six.string_types):
        # check for a remote source
        lower = source.lower()
        if  lower.startswith('http://') or \
            lower.startswith('https://') or \
            lower.startswith('file://') or \
            lower.startswith('ftp://'):
            response = urllib.urlopen(source)
            source = response.read()
        # ready to parse
        encoding = kwargs.get('encoding', 'UTF-8')
        secret = kwargs.get('secret', DEFAULT_SECRET)
        source = load_data(source, encoding=encoding, secret=secret)
    return source

def json_source_to_map(source, **kwargs):
    source = process_json_source(source, **kwargs)
    assert isinstance(source, Mapping)
    return CaseInsensitiveDict(source)

def issuer_from_source(source, **kwargs):
    data = json_source_to_map(source, **kwargs)
    result = model.IssuerOrganization()
    for field, func in (('name', _unicode), ('image', navstr), ('url', navstr),
                        ('email', _unicode), ('revocationList', navstr)):
        value = data.get(field)
        value = func(value) if value else None
        setattr(result, field, value)
    return result

def badge_from_source(source, **kwargs):
    data = json_source_to_map(source, **kwargs)
    result = model.BadgeClass()

    # parse common single value fields
    for field, func in (('name', _unicode),
                        ('description', _unicode), ('image', navstr),
                        ('criteria', navstr), ('issuer', navstr)):
        value = data.get(field)
        value = func(value) if value else None
        setattr(result, field, value)

    # tags
    result.tags = data.get('tags', ())

    # alignment objects
    result.alignment = alignment = []
    for data in data.get('alignment', ()):
        ao = model.AlignmentObject()
        ao.url = navstr(data['url'])
        ao.name = _unicode(data['name'])
        ao.description = _unicode(data.get('description'))
        alignment.append(ao)

    return result

def assertion_from_source(source, **kwargs):
    data = json_source_to_map(source, **kwargs)
    result = model.BadgeAssertion()

    # parse common single value fields
    for field, func in (('uid', _unicode), ('image', navstr), ('issuedOn', _datetime),
                        ('evidence', navstr), ('badge', navstr), ('expires', _datetime)):
        value = data.get(field)
        value = func(value) if value else None
        setattr(result, field, value)

    # recipient
    recipient = data['recipient']
    result.recipient = model.IdentityObject(type=_unicode(recipient['type']),
                                            identity=_unicode(recipient["identity"]),
                                            hashed=recipient.get('hashed', False),
                                            salt=_unicode(recipient.get("salt")))

    # verify
    verify = data['verify']
    result.verify = model.VerificationObject(type=verify["type"],
                                             url=navstr(verify['url']))

    return result
