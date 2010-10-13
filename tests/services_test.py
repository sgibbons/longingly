
import unittest

from longingly.services import LongURL
from longingly.error import ResolutionException
from longingly.fetcher import DefaultFetcher

from urlparse import urlparse

class TestLongURLService(unittest.TestCase):

	def setUp(self):

		self.service = LongURL(DefaultFetcher)

	
	def test_supports_shortener(self):

		real_shorteners = ['bit.ly', 'tinyurl.com', 'is.gd', 'short.ie']

		for shortener in real_shorteners:
			self.assertTrue(self.service.supports_shortener(shortener))
			
		fake_shorteners = ['fake.shortener', 'yahoo.com', 'slashdot.org']

		for shortener in fake_shorteners:
			self.assertFalse(self.service.supports_shortener(shortener))

	
	def test_expand(self):

		short_urls = map(lambda u: urlparse(u), ['http://tinyurl.com/2lekkm', 'http://bit.ly/97ecaX'])

		for url in short_urls:
			self.assertEqual('http://github.com', self.service.expand(url).geturl())


		self.assertRaises(ResolutionException, self.service.expand, urlparse('fake.shortener/foobar'))
		
		
