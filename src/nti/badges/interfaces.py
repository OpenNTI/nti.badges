#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface

from nti.base.interfaces import ICreatedTime

from nti.schema.field import Bool
from nti.schema.field import Number
from nti.schema.field import Object
from nti.schema.field import Variant
from nti.schema.field import TupleFromObject
from nti.schema.field import Text as ValidText
from nti.schema.field import DecodingValidTextLine as ValidTextLine


class Tag(ValidTextLine):
    """
    Requires its content to be only one plain text word that is lowercased.
    """

    def fromUnicode(self, value):
        return super(Tag, self).fromUnicode(value.lower())

    def constraint(self, value):
        return super(Tag, self).constraint(value)


class ITaggedContent(interface.Interface):
    """
    Something that can contain tags.
    """

    tags = TupleFromObject(title=u"Tags applied by the user.",
                           value_type=Tag(min_length=1, 
                                          title=u"A single tag",
                                          __name__=u'tags'),
                           unique=True,
                           default=(),
                           required=False)


class IBadgeIssuer(interface.Interface):
    """
    marker interface for all badge issuers
    """


class IBadgeAssertion(interface.Interface):
    """
    marker interface for all badge assertion
    """
    uid = ValidTextLine(title=u"The unique id of the assertion")


class IBadgeClass(interface.Interface):
    """
    marker interface for all badges
    """
    name = ValidTextLine(title=u"The name of the badge")


class INTIIssuer(IBadgeIssuer, ICreatedTime):

    name = ValidTextLine(title=u'Issuer name')

    origin = ValidTextLine(title=u'Issuer origin')

    organization = ValidTextLine(title=u'Issuer organization')

    email = ValidTextLine(title=u"Issuer email")


class INTIBadge(ITaggedContent,
                IBadgeClass,
                ICreatedTime):

    issuer = Object(INTIIssuer,
                    title=u"Badge Issuer",
                    required=False)

    name = ValidTextLine(title=u"Badge name")

    description = ValidText(title=u"Badge description",
                            required=False,
                            default=u'')

    image = ValidTextLine(title=u'Badge image identifier/URL')

    criteria = ValidTextLine(title=u'Badge criteria identifier/URL')


class INTIPerson(ICreatedTime):
    name = ValidTextLine(title=u"Person [unique] name")
    email = ValidTextLine(title=u"Person [unique] email")


class INTIAssertion(IBadgeAssertion):

    uid = ValidTextLine(title=u"Assertion id")

    badge = Object(INTIBadge, title=u"Badge")

    person = Variant((ValidTextLine(title=u"Badge recipient name/email"),
                      Object(INTIPerson, title=u"Badge recipient person")),
                     title=u"Badge recipient")

    issuedOn = Number(title=u"Date that the achievement was awarded",
                      default=0)

    recipient = ValidTextLine(title=u"Badge recipient email-hash", 
                              required=False)
    salt = ValidTextLine(title=u"One-way function to hash person", 
                         required=False)

    exported = Bool(title=u"If the assertion has been exported", 
                    default=False,
                    required=False)


class IEarnableBadge(interface.Interface):
    """
    marker interface for a earnable badbe
    """


class IEarnedBadge(IEarnableBadge):
    """
    marker interface for a earned badbe
    """


class IBadgeManager(interface.Interface):

    def person_exists(person=None, name=None):
        """
        check if a person exists
        """

    def get_person(person=None, email=None, name=None):
        """
        return a person
        """

    def update_person(person, email=None, name=None):
        """
        update a person
        """

    def badge_exists(badge):
        """
        check if the specifed badge exists
        """

    def add_badge(badge, issuer=None):
        """
        add the specifed badge
        """

    def update_badge(badge, description=None, criteria=None):
        """
        update the information regarding a batch
        """

    def get_badge(badge):
        """
        return the specifed badge
        """

    def get_all_badges():
        """
        return all available badges
        """

    def get_person_badges(person):
        """
        return the earned badges for the specified person
        """

    def get_assertion_by_id(assertion_id):
        """
        return the badge assertion for the specified id
        """

    def get_assertion(person, badge):
        """
        return a badge assertion for the specified person
        """

    def add_assertion(person, badge, exported=False):
        """
        add a badge assertion for the specified person
        """

    def update_assertion(uid, email=None, exported=True):
        """
        update an assertion
        """

    def remove_assertion(person, badge):
        """
        remove a badge assertion from the specified person
        """

    def assertion_exists(person, badge):
        """
        check if a badge assertion exists
        """

    def get_all_persons():
        """
        return all persons
        """

    def get_person_assertions(person):
        """
        return the assertions for the specified person
        """

    def delete_person(person):
        """
        delete the user w/ the specified person
        """

    def get_all_issuers():
        """
        return all issuers
        """

    def issuer_exists(issuer, origin=None):
        """
        return the specified issuer exists
        """

    def get_issuer(issuer, origin=None):
        """
        return the specified issuer
        """

    def add_issuer(issuer):
        """
        add the specified :class:`.IIssuer` object.
        """
