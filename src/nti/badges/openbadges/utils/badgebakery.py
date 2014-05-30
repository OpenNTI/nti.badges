#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
This small module makes it easy to bake PNG images with links to
Open Badge assertions. It also allows for easy retrieval of the link
from baked PNGs.

https://gist.github.com/toolness/5326379

.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from PIL import Image
from PIL import PngImagePlugin

from itsdangerous import JSONWebSignatureSerializer

from . import DEFAULT_SECRET

def get_baked_data(source):
	"""
	Return the assertion URL contained in the given baked PNG. If
	the image isn't baked, return None.

	Example:
		>>> get_baked_url('baked.png')
		'http://f.org/assertion.json'
	"""
	img = Image.open(source)
	meta = img.info
	result = meta.get('openbadges')
	return result

def bake_badge(source, target, url=None, payload=None, secret=DEFAULT_SECRET):
	"""
	Bake the given PNG file with the given assertion URL. The source and
	destination can be filenames or file objects.

	Example:

		>>> bake_badge('unbaked.png', 'baked.png', 'http://f.org/a.json')
	"""
	if url and payload:
		raise ValueError("must specify either an URL or payload")

	if payload and not secret:
		raise ValueError("must specify a valid JWS secret")
	
	data = url
	if payload:
		# “itsdangerous” only provides HMAC SHA derivatives and the none algorithm
		# at the moment and does not support the ECC based ones.
		jws = JSONWebSignatureSerializer(secret)
		data = jws.dumps(payload)

	source = Image.open(source)
	meta = PngImagePlugin.PngInfo()
	meta.add_text("openbadges", data)
	source.save(target, "png", pnginfo=meta)
