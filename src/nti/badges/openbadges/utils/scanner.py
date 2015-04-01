#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from ..interfaces import IBadgeClass
from ..interfaces import IIssuerOrganization

def get_baked_data(name, **kwargs):
	try:
		secret = kwargs.get('secret')
		data = badgebakery.get_baked_data(name, secret=secret)
		return data
	except Exception as e:
		logger.error("Could not get baked URL from '%s'; %s", name, e)

def parse_badge(source, verify=False, **kwargs):
	try:
		badge = badge_from_source(source, **kwargs)
		if verify:
			verifyObject(IBadgeClass, badge)
		return badge
	except Exception as e:
		logger.error("Could not parse badge data; %s", e)

def parse_issuer(source, verify=False):
	try:
		issuer = issuer_from_source(source)
		if verify:
			verifyObject(IIssuerOrganization, issuer)
		return issuer
	except Exception as e:
		logger.error("Could not parse issuer from '%s'; %s", source, e)

def flat_scan(path, verify=False, **kwargs):
	result = []
	issuers = {}
	path = os.path.expanduser(path)
	pathname = os.path.join(path, '*')
	for name in glob.iglob(pathname):
		name = os.path.join(path, name)
		_, ext = os.path.splitext(name)
		if ext.lower() != '.png' or not os.path.isfile(name):
			continue
		baked_data = get_baked_data(name, **kwargs)
		badge = parse_badge(baked_data, verify=verify, **kwargs) if baked_data else None
		if badge is None:
			continue
		logger.debug("Badge %s parsed", badge.name)
		issuer_url = (badge.issuer or u'').lower()
		issuer = issuers.get(issuer_url)
		if issuer is None:
			issuer = parse_issuer(issuer_url)
			issuers[issuer_url] = issuer
		result.append((badge, issuer))
	return result
