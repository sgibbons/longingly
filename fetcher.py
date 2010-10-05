import json

class Fetcher:

	def __init__(self, async = False):
		
		self.ASYNC = async


	def get(url, data):
		
		# Override in subclass
		raise NotImplementedException()


	def __get__(url, data, method, catch):

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

	from google.appengine.api import urlfetch


	def __init__(self, async = False):

		super(GoogleAppEngineFetcher, self).__init__(async)


	def get(url, data):

		self.__get__(url, data, lambda u: urlfetch.fetch(url).contents, urlfetch.DownloadError)
		

class DefaultFetcher(Fetcher):

	import urllib

	def __init__(self, async = False):

		super(DefaultFetcher, self).__init__(async)

	def get(url, data):
		
		self.__get__(url, data, lambda u: urllib.urlopen(u).read(), IOError)

			




		
