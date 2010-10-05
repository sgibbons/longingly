import json

class Fetcher:

	def get(self, url, data):
		
		# Override in subclass
		raise NotImplementedException()


	def __get__(self, url, data, method, catch):

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

	try:
		from google.appengine.api import urlfetch
	except ImportError:
		pass

	def get(self, url, data):

		return self.__get__(url, data, lambda u: urlfetch.fetch(url).contents, urlfetch.DownloadError)
		

class DefaultFetcher(Fetcher):

	try:
		import urllib
	except ImportError:
		pass

	def get(self, url, data):
		
		return self.__get__(url, data, lambda u: urllib.urlopen(u).read(), IOError)

			




		
