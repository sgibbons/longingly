import json
from error import ResolutionException

class Fetcher:

	def get(self, url, data):
		
		# Override in subclass
		raise NotImplementedException()


	def __get__(self, url, method, catch):

		try:
			json_results = method(url)

		except catch:
			raise ResolutionException('Could not connect to URL ' + url)

		else:
			
			try:
				return json.loads(json_results)

			except ValueError:
				raise ResolutionException('Could not parse JSON results')


class GoogleAppEngineFetcher(Fetcher):


	def get(self, url):

		try:
			from google.appengine.api import urlfetch
		except ImportError:
			pass
		else:
			return self.__get__(url, lambda u: urlfetch.fetch(url).contents, urlfetch.DownloadError)
		

class DefaultFetcher(Fetcher):


	def get(self, url):
		
		try:
			import urllib
		except ImportError:
			pass
		else:
			return self.__get__(url, lambda u: urllib.urlopen(u).read(), IOError)

