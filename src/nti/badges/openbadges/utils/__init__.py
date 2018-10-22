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
from datetime import datetime
from collections import Mapping
from six.moves import urllib_parse
from dateutil.parser import parse as dateutil_parse

try:
    from urllib.request import urlopen
except ImportError:  # pragma: no cover
    import urllib
    urlopen = urllib.urlopen

import simplejson

from requests.structures import CaseInsensitiveDict

from zope.interface.common.idatetime import IDateTime

from itsdangerous.exc import BadSignature

from itsdangerous.jws import JSONWebSignatureSerializer

from nti.badges._compat import text_

from nti.badges.openbadges.interfaces import IBadgeClass
from nti.badges.openbadges.interfaces import ID_TYPE_EMAIL

from nti.badges.openbadges.model import BadgeClass
from nti.badges.openbadges.model import BadgeAssertion
from nti.badges.openbadges.model import IdentityObject
from nti.badges.openbadges.model import AlignmentObject
from nti.badges.openbadges.model import IssuerOrganization
from nti.badges.openbadges.model import VerificationObject

#: Default web signature serializer secret
DEFAULT_SECRET = '!f^#GQ5md{)Rf&Z'

#: Valid schemes
VALID_SCHEMES = ('http', 'https', 'file', 'ftp', 'sftp')

logger = __import__('logging').getLogger(__name__)


def parse_datetime(s):
    if isinstance(s, six.string_types):
        for func in (dateutil_parse, IDateTime):
            try:
                result = func(s)
                if result is not None:
                    break
            except Exception:  # pylint: disable=broad-except
                result = None
    else:
        result = datetime.fromtimestamp(float(s))
    return result


def mend_url(url, **kwargs):
    base = kwargs.get('base') or kwargs.get('base_url')
    url = text_(url)
    if base:
        base = text_(base)
        path = urllib_parse.urlparse(url).path
        path = path[1:] if path.startswith('/') else path
        base = base + '/' if not base.endswith('/') else base
        url = urllib_parse.urljoin(base, path)
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
                except Exception:
                    raise ValueError("Bad source or signature")
            else:
                raise TypeError("Cannot process source data")
    elif isinstance(source, Mapping):
        result = source
    else:
        raise ValueError("Invalid source data")
    return result


def process_json_source(source, **kwargs):
    if hasattr(source, "read"):
        source = source.read()
    if isinstance(source, bytes):
        source = source.decode("utf-8")
    if isinstance(source, six.string_types):
        # check for a remote source
        lower = source.lower()
        result = urllib_parse.urlparse(lower)
        if result.scheme in VALID_SCHEMES:
            # pylint: disable=unused-variable
            __traceback_info__ = source
            logger.info('Getting json data from %s', source)
            response = urlopen(source)
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
    for field, func in (('url', text_),
                        ('name', text_),
                        ('email', text_),
                        ('image', text_),
                        ('description', text_),
                        ('revocationList', text_)):
        value = data.get(field)
        value = func(value) if value else None
        setattr(result, field, value)
    result.url = mend_url(result.url, **kwargs)
    return result


def badge_from_source(source, **kwargs):
    data = json_source_to_map(source, **kwargs)
    result = BadgeClass()

    # This should really go through the standard
    # nti.externalization process. As it is, we are clearly
    # rolling our own validation and transformation logic.

    # parse common single value fields
    for field, func in (('name', text_),
                        ('image', text_),
                        ('criteria', text_),
                        ('description', text_)):
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
    tags = [text_(x) for x in data.get('tags', ())]
    result.tags = IBadgeClass['tags'].bind(result).fromObject(tags)

    # alignment objects
    result.alignment = alignment = []
    for data in data.get('alignment', ()):
        ao = AlignmentObject()
        ao.url = data['url']
        ao.name = text_(data['name'])
        ao.description = text_(data.get('description'))
        alignment.append(ao)
    return result


def assertion_from_source(source, **kwargs):
    data = json_source_to_map(source, **kwargs)
    result = BadgeAssertion()

    # parse common single value fields
    for field, func in (('uid', text_),
                        ('image', text_),
                        ('evidence', text_),
                        ('expires', parse_datetime),
                        ('issuedOn', parse_datetime)):
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
        identity = text_(recipient)
        recipient = data
    else:
        identity = text_(recipient["identity"])

    salt = text_(recipient.get("salt"))
    hashed = recipient.get('hashed', True if salt else False)
    result.recipient = IdentityObject(type=ID_TYPE_EMAIL,
                                      identity=identity,
                                      hashed=hashed,
                                      salt=salt)

    # verify
    verify = data['verify']
    result.verify = VerificationObject(type=verify["type"],
                                       url=text_(verify['url']))

    return result
