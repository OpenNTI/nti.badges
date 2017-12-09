#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
  
# pylint: disable=inherit-non-class,arguments-differ
  
from zope import interface

from nti.badges.interfaces import IBadgeClass
from nti.badges.interfaces import IBadgeIssuer
from nti.badges.interfaces import IBadgeManager
from nti.badges.interfaces import IBadgeAssertion

from nti.schema.field import Int
from nti.schema.field import Bool
from nti.schema.field import ValidText
from nti.schema.field import ValidDatetime
from nti.schema.field import DecodingValidTextLine as ValidTextLine


class ITahrirModel(interface.Interface):
    """
    marker interface for Tahrir model objects
    """


class IIssuer(ITahrirModel, IBadgeIssuer):

    id = Int(title=u"Issuer id")

    origin = ValidTextLine(title=u"Issuer origin")

    name = ValidTextLine(title=u" Issuer name")

    org = ValidTextLine(title=u" Issuer organization")

    contact = ValidTextLine(title=u" Issuer contact")

    created_on = ValidDatetime(title=u"Created time")


class IBadge(ITahrirModel, IBadgeClass):

    name = ValidTextLine(title=u"Badge name")

    image = ValidTextLine(title=u"Image name/URL")

    description = ValidText(title=u"Badge description")

    criteria = ValidTextLine(title=u"Criteria URL")

    issuer_id = Int(title=u'Issuer id')

    created_on = ValidDatetime(title=u"Created time")

    tags = ValidTextLine(title=u" Badge tags")


class IPerson(ITahrirModel):

    id = Int(title=u"Person's id")

    email = ValidTextLine(title=u" Person's email")

    nickname = ValidTextLine(title=u" Person's nickname", required=False)

    website = ValidTextLine(title=u"Image name/URL")

    bio = ValidText(title=u"Person's bio", required=False)

    created_on = ValidDatetime(title=u"Created time")

    last_login = ValidDatetime(title=u"Last login", required=False)

    opt_out = Bool(title=u"Opt out flag", required=False)

    rank = Int(title=u"Person's rank", required=False)


class IInvitation(ITahrirModel):

    id = ValidTextLine(title=u" Invitation id")

    created_on = ValidDatetime(title=u"Created time")

    expires_on = ValidDatetime(title=u"Expiration time")

    badge_id = Int(title=u'Badge id')

    created_by = Int(title=u'Person id')


class IAuthorization(ITahrirModel):

    id = Int(title=u"Authorization's id")

    badge_id = ValidTextLine(title=u" Badge id")

    person_id = Int(title=u"Person id")


class IAssertion(ITahrirModel, IBadgeAssertion):

    id = ValidTextLine(title=u"Assertion id")

    badge_id = ValidTextLine(title=u"Badge id")

    person_id = Int(title=u"Person's id")

    salt = ValidTextLine(title=u"Salt")

    issued_on = ValidDatetime(title=u"Issue date")

    issued_for = ValidTextLine(title=u"Issue for", required=False)

    recipient = ValidTextLine(title=u"Recipient ", required=False)

    exported = Bool(title=u"If the assertion has been exported",
                    default=False,
                    required=False)


class ITahrirBadgeManager(IBadgeManager):
    """
    Interface for Tahrir database managers
    """

    defaultSQLite = interface.Attribute('SQLite attribute')

    scoped_session = interface.Attribute('Scoped session')

    def update_person(person, email=None, name=None, website=None, bio=None):
        """
        Update person information
        """

    def update_badge(badge, description=None, criteria=None, tags=None):
        """
        Update badge information
        """

    def get_issuer_by_id(issuer_id):
        """
        return the issuer by its id
        """

    def get_person_by_id(person_id):
        """
        return the person by its id
        """
