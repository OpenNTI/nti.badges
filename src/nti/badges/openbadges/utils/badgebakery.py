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

def get_baked_url(source):
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

def bake_badge(source, target, url):
	"""
	Bake the given PNG file with the given assertion URL. The source and
	destination can be filenames or file objects.

	Example:

		>>> bake_badge('unbaked.png', 'baked.png', 'http://f.org/a.json')
	"""

	source = Image.open(source)
	meta = PngImagePlugin.PngInfo()
	meta.add_text("openbadges", url)
	source.save(target, "png", pnginfo=meta)
