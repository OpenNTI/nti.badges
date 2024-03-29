#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This small module makes it easy to bake PNG images with links to
Open Badge assertions. It also allows for easy retrieval of the link
from baked PNGs.

https://gist.github.com/toolness/5326379

.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import argparse

from six.moves import urllib_parse

import simplejson

from PIL import Image
from PIL import PngImagePlugin

from itsdangerous.jws import JSONWebSignatureSerializer

logger = __import__('logging').getLogger(__name__)


def get_baked_data(source, secret=None, raw=False):
    """
    Return the assertion data contained in the given baked PNG. If
    the image isn't baked, return None.

    Example:
            >>> get_baked_url('baked.png')
            'http://f.org/assertion.json'
    """
    img = Image.open(source)
    meta = img.info
    result = meta.get('openbadges')
    if raw:
        return result

    # # check if it's a known scheme
    scheme = urllib_parse.urlparse(result).scheme if result else None
    if scheme:
        return result

    if result:
        if secret:
            try:
                jws = JSONWebSignatureSerializer(secret)
                data = jws.loads(result)
                result = data
            except Exception as e:  # pylint: disable=broad-except
                logger.error("Cannot load baked data. %s", e)
                result = None
        else:
            try:
                data = simplejson.loads(result, encoding="utf-8")
                result = data
            except Exception as e:  # pylint: disable=broad-except
                logger.error("Cannot load baked data. %s", e)
                result = None
    return result


def bake_badge(source, target, url=None, payload=None, secret=None):
    """
    Bake the given PNG file with the given assertion URL. The source and
    destination can be filenames or file objects.

    Example:

            >>> bake_badge('unbaked.png', 'baked.png', 'http://f.org/a.json')
    """
    if url and payload:
        raise ValueError("must specify either an URL or payload")

    data = url
    if payload:
        if secret:
            # “itsdangerous” only provides HMAC SHA derivatives and the none algorithm
            # at the moment and does not support the ECC based ones.
            jws = JSONWebSignatureSerializer(secret)
            data = jws.dumps(payload)
        else:
            data = simplejson.dumps(payload)

    # pylint: disable=unused-variable
    __traceback_info__ = data
    source = Image.open(source)
    meta = PngImagePlugin.PngInfo()
    meta.add_text("openbadges", data)
    source.save(target, "png", pnginfo=meta)


def process_args(args=None):
    arg_parser = argparse.ArgumentParser(description="Baked a badge")
    arg_parser.add_argument('-v', '--verbose', help="Verbose",
                            action='store_true',
                            dest='verbose')
    arg_parser.add_argument('source', help="The image to bake file path")
    arg_parser.add_argument('target', nargs='?', help="The baked image file path",
                            default=None)
    arg_parser.add_argument('-s', '--secret',
                            dest='secret',
                            default=None,
                            help="JSON web signature serializer secret")
    site_group = arg_parser.add_mutually_exclusive_group()
    site_group.add_argument('-u', '--url',
                            dest='url',
                            help="The badge URL")
    site_group.add_argument('-p', '--payload',
                            dest='payload',
                            help="The badge payload json file")

    args = arg_parser.parse_args(args=args)

    source = os.path.expanduser(args.source)
    if     not os.path.exists(source) or not os.path.isfile(source) \
        or not source.lower().endswith('.png'):
        print("Invalid image file", source, file=sys.stderr)
        return 2

    target = args.target
    if target is None:
        target = source
    target = os.path.expanduser(target)

    url = args.url
    payload = args.payload
    if payload:
        if not os.path.exists(payload):
            print("Payload file does not", payload, file=sys.stderr)
            return 2

        with open(payload, "r") as fp:
            payload = simplejson.load(fp)

    bake_badge(source, target, url=url, payload=payload, secret=args.secret)
    return 0


def main(args=None):  # pragma: no cover
    sys.exit(process_args(args))


if __name__ == '__main__':  # pragma: no cover
    main()
