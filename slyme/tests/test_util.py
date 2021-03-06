# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""unit tests"""

import sys, os
import unittest

import slyme
from slyme import util

import settings


class ShTestCase(unittest.TestCase):
	funky_string = r"""foo'bar "more" \' \" \n zzz"""
	funky_string_quoted = r"""'foo'\''bar "more" \'\'' \" \n zzz'"""

	#basic runsh()
	def test_runsh_string(self):
		self.assertEqual(util.runsh('/bin/echo foo'), 'foo\n',
			"runsh() does not work on sh code as a string"
		)
	def test_runsh_list(self):
		self.assertEqual(util.runsh(['/bin/echo','foo']), 'foo\n',
			"runsh() does not works on an argv list"
		)

	#runsh() with stdinstr
	def test_runsh(self):
		self.assertEqual(util.runsh('cat', inputstr='foo'), 'foo',
			"runsh does not work on sh code as a string, when providing stdin"
		)
	def test_runsh_with_stdin_list(self):
		"""That runsh_with_stdin() works on argv list."""
		self.assertEqual(util.runsh(['cat',], inputstr='foo'), 'foo',
			"runsh does not work on an argv list, when providing stdin"

		)

	#basic runsh_i()
	def test_runsh_i_string(self):
		self.assertEqual(
			[line for line in util.runsh_i("/bin/echo -e 'foo\nbar'")],
			['foo\n', 'bar\n'],
			"runsh_i() does not work on sh code as a string"
		)
	def test_runsh_list(self):
		self.assertEqual(
			[line for line in util.runsh_i(['/bin/echo', '-e', 'foo\nbar'])],
			['foo\n', 'bar\n'],
			"runsh_i() does not work on an argv list"
		)

	#shquote()
	def test_shquote(self):
		self.assertEqual(
			util.shquote(ShTestCase.funky_string),
			ShTestCase.funky_string_quoted,
			"quoting with shquote() is not the same as quoting manually"
		)
	def test_shquote_runsh(self):
		self.assertEqual(
			util.runsh('/bin/echo -n %s' % util.shquote(ShTestCase.funky_string)),
			ShTestCase.funky_string,
			"echo is not identity for a funky_string"
		)

	#sherrcheck()
	def test_sherrcheck_status(self):
		"""Test that a non-zero exit status raises an Exception."""
		try:
			util.runsh('exit 42')
		except util.ShError, e:
			self.assertEquals(e.returncode, 42,
				"ShError does not include proper returncode"
			)
		else:
			raise AssertionError("bash sh code did not raise proper exception")
	def test_sherrcheck_stderr(self):
		"""Test that non-empty stderr raises an Exception."""
		try:
			util.runsh('/bin/echo foo >&2')
		except util.ShError, e:
			self.assertEquals(e.stderr, 'foo\n',
				"ShError does not include proper stderr"
			)
		else:
			raise AssertionError("bash sh code did not raise proper exception")


if __name__=='__main__':
	unittest.main()
