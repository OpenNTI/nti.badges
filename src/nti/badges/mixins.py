#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from zope.mimetype.interfaces import IContentTypeAware

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IContentTypeAware)
class ContentTypeAwareMixin(object):

    parameters = dict()

    def __init__(self, *args, **kwargs):
        super(ContentTypeAwareMixin, self).__init__(*args, **kwargs)
