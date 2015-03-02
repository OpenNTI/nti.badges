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

from nti.common.maps import CaseInsensitiveDict

from ...utils import safestr

from .. import model
from .. import interfaces

DEFAULT_SECRET = u'!f^#GQ5md{)Rf&Z'

def _datetime(s):
	if isinstance(s, basestring):
		result = parse(s)
	else:
		result = datetime.fromtimestamp(float(s))
	return result

def load_data(source, encoding='UTF-8', secret=DEFAULT_SECRET):
	# We must decode the source ourself, to be a unicode
	# string; otherwise, simplejson may return us a dictionary
	# with byte objects in it, which is clearly wrong
	if isinstance(source, bytes):
		source = source.decode(encoding)

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
			__traceback_info__ = source
			logger.info('Getting json data from %s', source)
			response = urllib.urlopen(source)
			source = response.read()
		# ready to parse
		encoding = kwargs.get('encoding') or 'UTF-8'
		secret = kwargs.get('secret') or DEFAULT_SECRET
		source = load_data(source, encoding=encoding, secret=secret)
	return source

def json_source_to_map(source, **kwargs):
	source = process_json_source(source, **kwargs)
	assert isinstance(source, Mapping)
	return CaseInsensitiveDict(source)

def issuer_from_source(source, **kwargs):
	data = json_source_to_map(source, **kwargs)
	result = model.IssuerOrganization()
	for field, func in (('name', safestr), ('image', safestr), ('url', safestr),
						('email', safestr), ('revocationList', safestr),
						('description', safestr)):
		value = data.get(field)
		value = func(value) if value else None
		setattr(result, field, value)
	return result

def badge_from_source(source, **kwargs):
	data = json_source_to_map(source, **kwargs)
	result = model.BadgeClass()

	# XXX: This should really go through the standard
	# nti.externalization process. As it is, we are clearly
	# rolling our own validation and transformation logic.

	# parse common single value fields
	for field, func in (('name', safestr), ('description', safestr),
						('criteria', safestr), ('image', safestr)):
		value = data.get(field)
		value = func(value) if value else None
		setattr(result, field, value)

	# issuer
	issuer = data['issuer']
	result.issuer = issuer_from_source(issuer, **kwargs) \
					if isinstance(issuer, Mapping) else safestr(issuer)

	# tags
	tags = [safestr(x) for x in data.get('tags', ())]
	result.tags = type(result).__dict__['tags'].bind(result).fromObject(tags)

	# alignment objects
	result.alignment = alignment = []
	for data in data.get('alignment', ()):
		ao = model.AlignmentObject()
		ao.url = safestr(data['url'])
		ao.name = safestr(data['name'])
		ao.description = safestr(data.get('description'))
		alignment.append(ao)

	return result

def assertion_from_source(source, **kwargs):
	data = json_source_to_map(source, **kwargs)
	result = model.BadgeAssertion()

	# parse common single value fields
	for field, func in (('uid', safestr), ('image', safestr), ('issuedOn', _datetime),
						('evidence', safestr), ('expires', _datetime)):
		value = data.get(field)
		value = func(value) if value else None
		setattr(result, field, value)

	# badge
	badge = data['badge']
	result.badge = badge_from_source(badge, **kwargs) \
				   if isinstance(badge, Mapping) else safestr(badge)

	# recipient
	recipient = data['recipient']
	if not isinstance(recipient, Mapping):
		identity = safestr(recipient)
		recipient = data
	else:
		identity = safestr(recipient["identity"])

	salt = safestr(recipient.get("salt"))
	hashed = recipient.get('hashed', True if salt else False)
	result.recipient = model.IdentityObject(type=interfaces.ID_TYPE_EMAIL,
											identity=identity,
											hashed=hashed,
											salt=salt)

	# verify
	verify = data['verify']
	result.verify = model.VerificationObject(type=verify["type"],
											 url=safestr(verify['url']))

	return result
