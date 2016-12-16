#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os
import six
import urllib
from urlparse import urljoin
from urlparse import urlparse
from datetime import datetime
from collections import Mapping
from dateutil.parser import parse

import simplejson

from itsdangerous import BadSignature
from itsdangerous import JSONWebSignatureSerializer

from nti.badges.openbadges.interfaces import IBadgeClass
from nti.badges.openbadges.interfaces import ID_TYPE_EMAIL

from nti.badges.openbadges.model import BadgeClass
from nti.badges.openbadges.model import BadgeAssertion
from nti.badges.openbadges.model import IdentityObject
from nti.badges.openbadges.model import AlignmentObject
from nti.badges.openbadges.model import IssuerOrganization
from nti.badges.openbadges.model import VerificationObject

from nti.common.maps import CaseInsensitiveDict

from nti.common.string import to_unicode

#: Default web signature serializer secret
DEFAULT_SECRET = u'!f^#GQ5md{)Rf&Z'

#: Valid schemes
VALID_SCHEMES = ('http', 'https', 'file', 'ftp', 'sftp')

def _datetime(s):
	if isinstance(s, basestring):
		result = parse(s)
	else:
		result = datetime.fromtimestamp(float(s))
	return result

def mend_url(url, **kwargs):
	base = kwargs.get('base') or kwargs.get('base_url')
	url = to_unicode(url)
	if base:
		base = to_unicode(base)
		path = urlparse(url).path
		path = path[1:] if path.startswith('/') else path
		base = base + '/' if not base.endswith('/') else base
		url = urljoin(base, path)
	return url

def load_data(source, encoding='UTF-8', secret=None):
	# We must decode the source ourself, to be a unicode
	# string; otherwise, simplejson may return us a dictionary
	# with byte objects in it, which is clearly wrong
	if isinstance(source, bytes):
		source = source.decode(encoding)

	if isinstance(source, six.string_types):
		try:
			result = simplejson.loads(source, encoding=encoding)
		except simplejson.JSONDecodeError:
			if secret:
				jws = JSONWebSignatureSerializer(secret)
				try:
					result = jws.loads(source)
				except BadSignature:
					raise ValueError("Bad source signature")
				except:
					raise ValueError("Cannot load source data")
			else:
				raise TypeError("Cannot process source data")
	elif isinstance(source, Mapping):
		result = source
	else:
		raise TypeError("Cannot process source data")
	return result

def process_json_source(source, **kwargs):
	if hasattr(source, "read"):
		source = source.read()
	if isinstance(source, six.string_types):
		# check for a remote source
		lower = source.lower()
		result = urlparse(lower)
		if result.scheme in VALID_SCHEMES:
			__traceback_info__ = source
			logger.info('Getting json data from %s', source)
			response = urllib.urlopen(source)
			source = response.read()
		# check for a local file
		elif os.path.exists(source) and os.path.isfile(source):
			with open(source, "r") as fp:
				source = fp.read()
		# ready to parse
		secret = kwargs.get('secret')
		encoding = kwargs.get('encoding') or 'UTF-8'
		source = load_data(source, encoding=encoding, secret=secret)
	return source

def json_source_to_map(source, **kwargs):
	source = process_json_source(source, **kwargs)
	assert isinstance(source, Mapping)
	return CaseInsensitiveDict(source)

def issuer_from_source(source, **kwargs):
	data = json_source_to_map(source, **kwargs)
	result = IssuerOrganization()
	for field, func in (('name', to_unicode), ('image', to_unicode), ('url', to_unicode),
						('email', to_unicode), ('revocationList', to_unicode),
						('description', to_unicode)):
		value = data.get(field)
		value = func(value) if value else None
		setattr(result, field, value)
	result.url = mend_url(result.url, **kwargs)
	return result

def badge_from_source(source, **kwargs):
	data = json_source_to_map(source, **kwargs)
	result = BadgeClass()

	# XXX: This should really go through the standard
	# nti.externalization process. As it is, we are clearly
	# rolling our own validation and transformation logic.

	# parse common single value fields
	for field, func in (('name', to_unicode), ('description', to_unicode),
						('criteria', to_unicode), ('image', to_unicode)):
		value = data.get(field)
		value = func(value) if value else None
		setattr(result, field, value)
	result.criteria = mend_url(result.criteria, **kwargs)

	# issuer
	issuer = data['issuer']
	if isinstance(issuer, Mapping):
		result.issuer = issuer_from_source(issuer, **kwargs)
	else:
		result.issuer = mend_url(issuer, **kwargs)

	# tags
	tags = [to_unicode(x) for x in data.get('tags', ())]
	result.tags = IBadgeClass['tags'].bind(result).fromObject(tags)

	# alignment objects
	result.alignment = alignment = []
	for data in data.get('alignment', ()):
		ao = AlignmentObject()
		ao.url = data['url']
		ao.name = to_unicode(data['name'])
		ao.description = to_unicode(data.get('description'))
		alignment.append(ao)
	return result

def assertion_from_source(source, **kwargs):
	data = json_source_to_map(source, **kwargs)
	result = BadgeAssertion()

	# parse common single value fields
	for field, func in (('uid', to_unicode), ('image', to_unicode), ('issuedOn', _datetime),
						('evidence', to_unicode), ('expires', _datetime)):
		value = data.get(field)
		value = func(value) if value else None
		setattr(result, field, value)

	# badge
	badge = data['badge']
	if isinstance(badge, Mapping):
		result.badge = badge_from_source(badge, **kwargs)
	else:
		result.badge = mend_url(badge, **kwargs)

	# recipient
	recipient = data['recipient']
	if not isinstance(recipient, Mapping):
		identity = to_unicode(recipient)
		recipient = data
	else:
		identity = to_unicode(recipient["identity"])

	salt = to_unicode(recipient.get("salt"))
	hashed = recipient.get('hashed', True if salt else False)
	result.recipient = IdentityObject(type=ID_TYPE_EMAIL,
									  identity=identity,
									  hashed=hashed,
									  salt=salt)

	# verify
	verify = data['verify']
	result.verify = VerificationObject(type=verify["type"],
									   url=to_unicode(verify['url']))

	return result
