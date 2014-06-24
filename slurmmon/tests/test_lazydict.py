# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""unit tests"""

import time
import unittest, mock

try:
	import slurmmon
except ImportError:
	sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
	import slurmmon
from slurmmon import lazydict


#--- an example LazyDict

class x_age(lazydict.Extension):
	source= ('birthdate',)
	target = ('age',)
	def __call__(cls, birthdate):
		return time.time() - birthdate,

class x_math(lazydict.Extension):
	source= ('x', 'y',)
	target = ('sum', 'diff',)
	def __call__(cls, x, y):
		return x+y, x-y

class x_identity(lazydict.Extension):
	source= ('name',)
	target = ('name_copy',)
	def __call__(self, name):
		return name,

class ExampleLazyDict(lazydict.LazyDict):
	keys = [
		#--- primary

		'name',
		#a string

		'birthdate',
		#a float, seconds since the epoch

		'x',
		#an int
		
		'y',
		#an int


		#--- derived

		'age',
		#an float, seconds since birthdate
		
		'sum',
		#x+y
		
		'diff',
		#x-y

		'name_copy',
		#just a copy of the name
	]

	primary_key = 'name'

	extensions = [
		x_age(),
		x_math(),
		x_identity(),
	]


#--- TestCases

class LazyDictTestCase(unittest.TestCase):
	def setUp(self):
		#--- inputs

		self.in_name = 'John Smith'

		tstr   = '1976-07-01 12:34:56.789012'
		format = '%Y-%m-%d %H:%M:%S.%f'
		self.in_birthdate = time.mktime(time.strptime(tstr, format))

		self.in_x = 5
		self.in_y = 3


		#--- expected outputs

		self.out_age = time.time() - self.in_birthdate

		self.out_sum = 8
		self.out_diff = 2


	#--- low-level extension calls

	def test_extension_one_to_one(self):
		e = x_age()
		
		age = e(self.in_birthdate)[0]

		self.assertAlmostEqual(
			age,
			self.out_age,
			places=0,
		)

	def test_extension_many_to_many(self):
		e = x_math()

		sum, diff = e(self.in_x, self.in_y)

		self.assertEqual(
			sum,
			self.out_sum
		)
		self.assertEqual(
			diff,
			self.out_diff
		)
	

	#--- fundamental LazyDict operation

	def test_creation(self):
		#most simple
		d = ExampleLazyDict(name=self.in_name)

		#with additional data
		d = ExampleLazyDict(name=self.in_name, birthdate=self.in_birthdate)
	
	def test_getitem_extension_one_to_one(self):
		d = ExampleLazyDict(name=self.in_name, birthdate=self.in_birthdate)
		
		self.assertAlmostEqual(
			d['age'],
			self.out_age,
			places=0,
		)
	
	def test_getitem_extension_many_to_many(self):
		d = ExampleLazyDict(name=self.in_name, x=self.in_x, y=self.in_y)

		self.assertEqual(
			d['sum'],
			self.out_sum,
		)
		self.assertEqual(
			d['diff'],
			self.out_diff,
		)
	
	def test_getitem_not_available(self):
		#note no birthdate, therefore not possible compute age by extension
		d = ExampleLazyDict(name=self.in_name)
		self.assertRaises(KeyError, d.__getitem__, 'age')
	
	def test_getitem_bad_key(self):
		#note no birthdate, therefore not possible compute age by extension
		d = ExampleLazyDict(name=self.in_name)

		self.assertRaises(KeyError, d.__getitem__, 'this-is-not-a-known-key')
	
	def test_getitem_identity_extension(self):
		d = ExampleLazyDict(name=self.in_name)
		self.assertEqual(
			d['name'],
			d['name_copy'],
		)


	##took away this complexity
	##--- str() etc.
	#
	#def test_str_with_pk(self):
	#	"""With a primary key, str() only reports the primary_key value."""
	#	class X(lazydict.LazyDict):
	#		keys = [
	#			'id',
	#			'foo',
	#		]
	#		primary_key = 'id'
	#
	#	x = X()
	#
	#	self.assertEqual(
	#		str(x),
	#		"<id None>",
	#	)
	#
	#	x['id'] = 42
	#	self.assertEqual(
	#		str(x),
	#		"<id 42>",
	#	)
	#
	#	self.assertEqual(
	#		repr(x),
	#		"{'id': 42}",
	#	)
	#
	#def test_str_without_pk(self):
	#	"""Without a primary key, str dumps the full dict."""
	#	class X(lazydict.LazyDict):
	#		keys = [
	#			'foo',
	#		]
	#
	#	x = X()
	#	
	#	self.assertEqual(
	#		str(x),
	#		"<{}>",
	#	)
	#
	#	x['foo'] = 42
	#	self.assertEqual(
	#		str(x),
	#		"<{'foo': 42}>",
	#	)
	

	#--- performance and laziness

	def test_getitem_extension_done_once(self):
		"""Test that the an extension is computed only once."""
		d = ExampleLazyDict(name=self.in_name, birthdate=self.in_birthdate)
		
		count = d._extension_count  #(class var, so this will have been jacked up by other instances)
		
		d['age']
		self.assertEqual(
			d._extension_count,
			count+1,  #i.e. one more
		)
		d['age']
		self.assertEqual(
			d._extension_count,
			count+1,  #i.e. no change
		)

	def test_getitem_extension_count_query_optimized(self):
		"""Test that the an extension is computed only once."""
		d = ExampleLazyDict(name=self.in_name, x=self.in_x, y=self.in_y)
		d.set_laziness(lazydict.LazyDict.LAZINESS_QUERY_OPTIMIZED)  #(the default)
		
		count = d._extension_count  #(class var, so this will have been jacked up by other instances)

		d['sum']  #this should store 'diff', too
		self.assertEqual(
			d._extension_count,
			count+1,  #i.e. one more
		)

		d['diff']  #this should have already been there
		self.assertEqual(
			d._extension_count,
			count+1,  #i.e. no more
		)

	def test_getitem_extension_count_data_optimized(self):
		"""Test that the an extension is computed only once."""
		d = ExampleLazyDict(name=self.in_name, x=self.in_x, y=self.in_y)
		d.set_laziness(lazydict.LazyDict.LAZINESS_DATA_OPTIMIZED)  #(the default)
		
		count = d._extension_count  #(class var, so this will have been jacked up by other instances)

		d['sum']  #this should NOT store 'diff', too
		self.assertEqual(
			d._extension_count,
			count+1,  #i.e. one more
		)

		d['diff']  #this will have to re-run the extension
		self.assertEqual(
			d._extension_count,
			count+2,  #i.e. one more
		)


if __name__=='__main__':
	unittest.main()
