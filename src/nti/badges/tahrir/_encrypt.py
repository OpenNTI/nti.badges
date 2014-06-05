#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Recipes to decrypt and encrypt passwords and related data.

See http://ejohn.org/blog/keeping-passwords-in-source-control/

File Format
===========

We are duplicating the OpenSSL file format, which is reverse engineered to be
the following::

  'Salted__' + ........ + ciphertext

where ``........`` is the 8 byte salt. The 16-byte key and 8 byte IV are
derived from the passphrase combined with the salt (the IV is not stored
in the file)::

  Key = MD5( passphrase + salt )
  IV  = MD5( key + passphrase + salt )[:8]

That is, the key is the MD5 checksum of concatenating the passphrase
followed by the salt, and the initial vector is the first 8 bytes of the
MD5 of the key, passphrase and salt concatenated.

$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os

from cStringIO import StringIO
from ConfigParser import SafeConfigParser as ConfigParser

try:
	from Crypto import Random
	from Crypto.Cipher import CAST
except ImportError:
	CAST = None
	Random = None

from hashlib import md5

class _BaseFormat(object):

	# : Eight bytes of random salt data
	salt = None

	def new_salt(self):
		return Random.new().read(CAST.block_size)

	def make_key(self, passphrase):
		if isinstance(passphrase, unicode):
			passphrase = passphrase.encode("utf-8")
		return md5(passphrase + self.salt).digest()

	def make_iv(self, passphrase):
		key = self.make_key(passphrase)
		if isinstance(passphrase, unicode):
			passphrase = passphrase.encode('utf-8')
		return md5(key + passphrase + self.salt).digest()[:8]

	def _make_cipher(self, passphrase):
		key = self.make_key(passphrase)
		iv = self.make_iv(passphrase)
		cipher = CAST.new(key, CAST.MODE_CBC, iv)
		return cipher

	def make_ciphertext(self, passphrase, plaintext):
		if isinstance(plaintext, unicode):
			plaintext = plaintext.encode('utf-8')
		return self._make_cipher(passphrase).encrypt(plaintext)

	def get_plaintext(self, passphrase, ciphertext):
		if CAST is not None:
			return self._make_cipher(passphrase).decrypt(ciphertext)
		return ''

def _read(name, mode):
	with open(name, mode) as f:
		return f.read()

class _EncryptedFile(_BaseFormat):

	def __init__(self, name):
		self.name = name
		self._data = _read(name, 'rb')
		if not self._data.startswith(b'Salted__'):
			raise ValueError("Improper input file format")

	@property
	def checksum(self):
		# In a format just like the md5sum command line program. Must be bytes
		csum = md5(self._data).hexdigest()
		basename = os.path.basename(self.name)
		return csum + b'  ' + basename + b'\n'

	@property
	def salt(self):
		return self._data[8:16]

	@property
	def ciphertext(self):
		return self._data[16:]

class _BaseDecrypt(object):

	plaintext = None

	def __init__(self, input_file, passphrase):

		if not input_file.endswith('.cast5'):
			raise ValueError("Input is not a .cast5 file")
		
		input_file = os.path.abspath(input_file)
		if not os.path.isfile(input_file):
			raise ValueError("Input file '%s' does not exist" % input_file)

		self._do_decrypting(input_file, passphrase)

	def _do_decrypting(self, input_file, passphrase):
		self._encrypted_file = _EncryptedFile(input_file)
		self.plaintext = \
				self._encrypted_file.get_plaintext(passphrase,
												   self._encrypted_file.ciphertext)
		# Cast5 CBC is a block cipher with an 8-byte block size.
		# The plaintext is always padded to be a multiple of 8
		# bytes by OpenSSL. If one byte is required, the padding
		# is \x01. If two bytes, \x02\x02, three bytes
		# \x03\x03\x03 and so on. If no bytes were required
		# because the input was the perfect size, then an entire
		# block of \x08 is added, so there is always padding to
		# remove.
		for pad in (chr(i) * i for i in range(8, 0, -1)):
			if self.plaintext.endswith(pad):
				self.plaintext = self.plaintext[:-len(pad)]
				break

class DecryptSection(_BaseDecrypt):

	options = None

	def __init__(self, input_file, passphrase, name):
		super(DecryptSection, self).__init__(input_file, passphrase)
		if self.plaintext:
			self._do_parse(self.plaintext, name)

	def _do_parse(self, plaintext, name):
		self.options = {}
		config = ConfigParser()
		config.readfp(StringIO(plaintext))
		for key, value in config.items(name):
			self.options[key] = value

class DecryptFile(_BaseDecrypt):

	def __init__(self, input_file, passphrase, output_file):
		super(DecryptFile, self).__init__(input_file, passphrase)
		if self.plaintext:
			self._do_write(self.plaintext, output_file)

	def _do_write(self, plaintext, output_file):
		with open(self.output_file, 'wb') as f:
			f.write(self.plaintext)
