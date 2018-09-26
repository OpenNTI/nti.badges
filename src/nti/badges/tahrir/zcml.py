#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class

import functools

from zope import interface

from zope.component.zcml import utility

from zope.schema import Bool
from zope.schema import TextLine

from nti.badges._compat import text_

from nti.badges.tahrir.interfaces import IIssuer
from nti.badges.tahrir.interfaces import ITahrirBadgeManager

from nti.badges.tahrir.manager import create_issuer
from nti.badges.tahrir.manager import create_badge_manager

logger = __import__('logging').getLogger(__name__)


class IRegisterTahrirDB(interface.Interface):
    """
    The arguments needed for registering an Tahri db
    """
    dburi = TextLine(title=u"db dburi", required=False)

    salt = TextLine(title=u'assertion salt', required=False)

    autocommit = Bool(title=u'autocommit option',
                      required=False,
                      default=False)

    twophase = Bool(title=u'two phase commit protocol',
                    required=False,
                    default=False)

    defaultSQLite = Bool(title=u'default to SQLLite',
                         required=False,
                         default=False)

    config = TextLine(title=u'path to a config file', required=False)


def registerTahrirDB(_context, dburi=None, twophase=False, salt=None,
                     autocommit=False, defaultSQLite=False, config=None):
    """
    Register an db
    """

    if not dburi and not defaultSQLite and not config:
        raise ValueError("must specified valid database uri")

    factory = functools.partial(create_badge_manager,
                                dburi=text_(dburi),
                                salt=text_(salt),
                                twophase=twophase,
                                autocommit=autocommit,
                                defaultSQLite=defaultSQLite,
                                config=text_(config))
    utility(_context, provides=ITahrirBadgeManager, factory=factory, name="")


class IRegisterTahrirIssuer(interface.Interface):
    """
    The arguments needed for registering a Tahri issuer
    """
    name = TextLine(title=u"Issuer [unique] name")

    origin = TextLine(title=u"Issuer origin [URL]")

    org = TextLine(title=u"Issuer organization [URL]")

    contact = TextLine(title=u"Issuer contact")

    id = TextLine(title=u"Issuer zcml identifier",
                  required=False,
                  default=u'')


def registerTahrirIssuer(_context, name, origin, org, contact, id=''):
    """
    Register a Tahri issuer
    """
    factory = functools.partial(create_issuer,
                                name=text_(name),
                                origin=text_(origin),
                                org=text_(org),
                                contact=text_(contact))
    utility(_context, provides=IIssuer, factory=factory, name=id)
