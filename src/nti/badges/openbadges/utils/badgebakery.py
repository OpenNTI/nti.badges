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

import png

def get_baked_url(src):
	"""
	Return the assertion URL contained in the given baked PNG. If
	the image isn't baked, return None.

	Example:
		>>> get_baked_url('baked.png')
		'http://f.org/assertion.json'
	"""

	if isinstance(src, basestring): src = open(src, 'rb')
	reader = png.Reader(file=src)
	for chunktype, content in reader.chunks():
		if chunktype == 'tEXt' and content.startswith('openbadges\x00'):
			return content.split('\x00')[1]

def bake_badge(src, dest, url):
	"""
	Bake the given PNG file with the given assertion URL. The source and
	destination can be filenames or file objects.

	Example:

		>>> bake_badge('unbaked.png', 'baked.png', 'http://f.org/a.json')
	"""

	if isinstance(src, basestring): src = open(src, 'rb')
	if isinstance(dest, basestring): dest = open(dest, 'wb')

	reader = png.Reader(file=src)
	chunks = [
		(chunktype, content)
		for chunktype, content in reader.chunks()
		if not (chunktype == 'tEXt' and content.startswith('openbadges\x00'))
	]

	chunks.insert(1, ('tEXt', '\x00'.join(('openbadges', url))))
	png.write_chunks(dest, chunks)
