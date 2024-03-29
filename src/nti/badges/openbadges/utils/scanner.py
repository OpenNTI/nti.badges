#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import six
import glob
import codecs

from zope.interface.verify import verifyObject

from nti.badges.openbadges.interfaces import IBadgeClass
from nti.badges.openbadges.interfaces import IIssuerOrganization

from nti.badges.openbadges.utils import badgebakery
from nti.badges.openbadges.utils import badge_from_source
from nti.badges.openbadges.utils import issuer_from_source

logger = __import__('logging').getLogger(__name__)


def get_baked_data(name, **kwargs):
    try:
        secret = kwargs.get('secret')
        data = badgebakery.get_baked_data(name, secret=secret)
        return data
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Could not get baked URL from '%s'; %s", name, e)


def parse_badge(source, verify=False, **kwargs):
    try:
        badge = badge_from_source(source, **kwargs)
        if verify:
            verifyObject(IBadgeClass, badge)
        return badge
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Could not parse badge data; %s", e)


def parse_issuer(source, verify=False):
    try:
        issuer = issuer_from_source(source)
        if verify:
            verifyObject(IIssuerOrganization, issuer)
        return issuer
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Could not parse issuer from '%s'; %s", source, e)


def get_issuer_url(issuer):
    if isinstance(issuer, six.string_types):
        result = issuer
    elif IIssuerOrganization.providedBy(issuer):
        result = issuer.url
    else:
        result = str(issuer) if issuer else None
    return result.lower() if result else ''


def flat_scan(path, verify=False, **kwargs):
    result = []
    issuers = {}
    cwd = os.getcwd()
    try:
        path = os.path.expanduser(path)
        os.chdir(path)  # change path
        pathname = os.path.join(path, '*')
        for name in glob.iglob(pathname):
            name = os.path.join(path, name)
            _, ext = os.path.splitext(name)
            if ext.lower() != '.json' or not os.path.isfile(name):  # pragma: no cover
                continue

            # parse badge json file
            with codecs.open(name, "r", encoding="utf-8") as fp:
                badge = parse_badge(fp, verify=verify, **kwargs)
            if badge is None:
                continue
            # pylint: disable=no-member
            logger.debug("Badge %s parsed", badge.name)

            issuer = badge.issuer
            if not isinstance(issuer, six.string_types):
                issuer_url = get_issuer_url(issuer)
                if issuer_url not in issuers:
                    issuers[issuer_url] = issuer
            else:
                issuer_url = issuer

            issuer = issuers.get(issuer_url)
            if issuer is None:
                issuer = parse_issuer(issuer_url)
                issuers[issuer_url] = issuer
            result.append((badge, issuer))
        return result
    finally:
        os.chdir(cwd)
