#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import has_entry
from hamcrest import assert_that

import os
import shutil
import tempfile
import unittest

from nti.badges.tahrir._encrypt import DecryptSection

class TestDecryptSection(unittest.TestCase):

	def test_decrypt_data(self):
		tmp_dir = tempfile.mkdtemp(dir="/tmp")
		try:
			ciphertext = (b'Salted__\xbe\x82\x11\xc4\x01\xe6\x94\xfc\x93\xb5\x8aF\xeb\x8chEy"'
						  b'\xd0\xb4\x04\xf3g\xb3.UX\x18\x17\x95\xe7 x7\x16\xa4{\x805~z\xe5\xad\xdc\xc4\xdc'
						  b'\xd43\x8e\xfd\xda\x108\xbfv\xf8yW\x1f\xd2\xd73j\x0f\xce\x0f(4\x95\xe3{&~{\xdf'
						  b'\x8ekm\xbb\x01\x17\xf28\x97\xd4\xfaSL\x99\xb5I\xfb\xc4\t\xb8\xeeH\x97\x02\\\xc8\xd6dw')
	
			cipher_file = os.path.join(tmp_dir, 'foo.cast5')
			with open(cipher_file, 'wb') as fp:
				fp.write(ciphertext)

			ds = DecryptSection(cipher_file, 'temp001', 'passwords')
			assert_that(ds.options, has_entry('smtp_passwd', 'Aoqcfbbec3grUZyUT0xzlkceVUy+aM+KbQYny6L1zz+i'))
			assert_that(ds.options, has_entry('sql_passwd', 'rdstemp001'))
		finally:
			shutil.rmtree(tmp_dir, True)
