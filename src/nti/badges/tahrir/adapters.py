#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import time

from zope import component
from zope import interface

from . import interfaces
from ..model import NTIBadge
from ..model import NTIIssuer
from .. import interfaces as badges_intefaces

@component.adapter(interfaces.IIssuer)
@interface.implementer(badges_intefaces.INTIIssuer)
def issuer_to_ntiissuer(issuer):
    result = NTIIssuer(uri=issuer.name, org=issuer.org)
    return result

@component.adapter(interfaces.IBadge)
@interface.implementer(badges_intefaces.INTIBadge)
def badge_to_ntibadge(badge):
    tags = tuple(x.lower() for x in ((badge.tags or u'').split(',')))
    result = NTIBadge(name=badge.name,
                      image=badge.image,
                      description=badge.description,
                      criteria=badge.criteria,
                      issuer=badges_intefaces.INTIIssuer(badge.issuer),
                      createdTime=time.mktime(badge.created_on.timetuple()),
                      tags=tags)
    return result
