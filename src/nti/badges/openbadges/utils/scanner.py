#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os
import glob

from zope.interface.verify import verifyObject

from . import badgebakery
from . import badge_from_source
from . import issuer_from_source
from .. import interfaces as open_interfaces

def _fix_url(url):
	if not url:
		return None
	for k,v in os.environ.items():
		url = url.replace('$' + k, v)
	return url

def get_baked_url(name):
	try:
		url = badgebakery.get_baked_url(name)
		return _fix_url(url)
	except Exception as e:
		logger.error("Could not get baked URL from '%s'; %s", name, e)

def parse_badge(name, verify=False):
	try:
		badge = badge_from_source(name)
		print(badge, name)
		if verify:
			verifyObject(open_interfaces.IBadgeClass, badge)
		return badge
	except Exception as e:
		print('FUCK', e)
		logger.error("Could not parse badge from '%s'; %s", name, e)

def parse_issuer(source, verify=False):
	try:
		issuer = issuer_from_source(source)
		if verify:
			verifyObject(open_interfaces.IIssuerOrganization, issuer)
		return issuer
	except Exception as e:
		logger.error("Could not parse issuer from '%s'; %s", source, e)

def flat_scan(path, verify=False):
	result = []
	issuers = {}  # cache
	path = os.path.expanduser(path)
	pathname = os.path.join(path, '*')
	for name in glob.iglob(pathname):
		name = os.path.join(path, name)
		_, ext = os.path.splitext(name)
		if ext.lower() != '.png' or not os.path.isfile(name):
			continue
		name = os.path.join(path, name)
		baked_url = get_baked_url(name)
		badge = parse_badge(baked_url, verify) if baked_url else None
		if badge is None:
			continue
		logger.debug("Badge %s parsed", badge.name)
		issuer_url = _fix_url((badge.issuer or u'').lower())
		issuer = issuers.get(issuer_url)
		if issuer is None:
			issuer = parse_issuer(issuer_url)
			issuers[issuer_url] = issuer
		result.append((badge, issuer))
	return result
