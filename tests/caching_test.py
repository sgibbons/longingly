import longingly.caching

import unittest

class TestDefaultCache(unittest.TestCase):

	def setUp(self):
		self.cache = longingly.caching.DefaultCache()

	def test_put(self):
		
		self.cache.put('foo', 'bar')

		self.assertTrue(self.cache.has_key('foo'))
		self.assertEqual(self.cache.get('foo'), 'bar')

		self.cache.put('foo', 'baz')

		self.assertTrue(self.cache.has_key('foo'))
		self.assertEqual(self.cache.get('foo'), 'baz')


	def test_has_key(self):

		self.assertFalse(self.cache.has_key('foo'))

		self.cache.put('foo', 'bar')

		self.assertTrue(self.cache.has_key('foo'))
		self.assertFalse(self.cache.has_key('bar'))

	
	def test_get(self):

		self.assertRaises(KeyError, self.cache.get, 'foo')

		self.cache.put('foo', 'bar')

		self.assertEqual(self.cache.get('foo'), 'bar')

		self.assertRaises(KeyError, self.cache.get, 'bar')

