import re
from urlparse import urlparse
from error import ResolutionException

class Service:
	
	def __init__(self, fetcher, priority = 0):
		
		self.SUPPORTS_BATCH = False
		self.MAX_BATCH_SIZE = 0
		self.priority = priority
		self.fetcher = fetcher()
		
		
	def expand(self, url_string):
		raise NotImplementedError()
	
	def batch_expand(self, url_strings):	
		raise NotImplementedError()
	
	def supports_shortener(self, domain):
		raise NotImplementedError()
	

class Bitly(Service):
	
	def __init__(self, fetcher, login, api_key, priority = 0):
		
		Service.__init__(self, fetcher, priority = priority)
		
		self.SUPPORTS_BATCH = True
		self.BASE_URL = 'http://api.bit.ly/v3/'
		self.AUTH_QUERY = '&login=' + login + '&apiKey=' + api_key
		self.MAX_BATCH_SIZE = 15
		
		
	def supports_shortener(self, domain):
		
		# short circuit for non-pro domains
		if domain == 'bit.ly':
			return True

		# hit the api to see if the domain is a supported pro domain
		# TODO: implement some kind of caching to avoid making repeated api calls
		result_dict = self.fetcher.get(self.BASE_URL + 'bitly_pro_domain?domain=' + domain + '&format=json' + self.AUTH_QUERY)['data']

		return result_dict.has_key('bitly_pro_domain') and result_dict['bitly_pro_domain']
	

	def expand(self, url):
		
		shorturl_string = url.geturl()

		expands =  self.fetcher.get(self.BASE_URL + 'expand?shortUrl=' + shorturl_string + '&format=json' + self.AUTH_QUERY)['data']['expand']
		for expansion in expands:
			if expansion['short_url'] == shorturl_string:
				return urlparse(expansion['long_url'])

		raise ResolutionException('Failed to resolve given URL: ' + shorturl_string)


	def batch_expand(self, batch):

		batch_strings = map(lambda u: u.geturl(), batch)

		batch_query = self.BASE_URL + 'expand?format=json'
		for shorturl in batch_strings:
			batch_query += '&shortUrl=' + shorturl

		expands = self.fetcher.get(batch_query + self.AUTH_QUERY)['data']['expand']

		filtered_expands = filter(lambda e: e['short_url'] in batch_strings, expands)
		result_dict = dict()
		for expansion in filtered_expands:

			# check to see that this was a successful expansion
			if expansion['short_url'] in batch_strings and not expansion.has_key('long_url'):
				raise ResolutionException('At least one of the supplied short urls (' + expansion['short_url'] + ') could not be resolved')

			# success, add the result to the dictionary
			result_dict[urlparse(expansion['short_url'])] = urlparse(expansion['long_url'])

		return result_dict
		

class LongURLPlease(Service):
	
	def __init__(self, fetcher, priority = 0):
		
		Service.__init__(self, fetcher, priority = priority)
		
		self.SUPPORTS_BATCH = True
		self.BASE_URL = 'http://www.longurlplease.com/api/'
		self.MAX_BATCH_SIZE = 15
		
		self.SUPPORTED_SHORTENERS = self.load_supported_services()
		
	
	# load the regex for shortener support from the longurlplease api
	def load_supported_services(self):
		
		return self.fetcher.get(self.BASE_URL + 'supported-services.json')['services']
	
		
	def supports_shortener(self, domain):
		
		return domain in self.SUPPORTED_SHORTENERS
			

	def expand(self, url):
		
		urlstring = url.geturl()
		
		result_dict = self.fetcher.get(self.BASE_URL + 'v1.1?q=' + urlstring)

		if result_dict.has_key(urlstring):
			return urlparse(result_dict[urlstring])
		else:
			raise ResolutionException("Failed to resolve the given URL " + urlstring)
	
	
	def batch_expand(self, batch):
		
		# [Url] -> [String]
		batch_strings = map(lambda u: u.geturl(), batch)
		
		# construct request string
		request_string = self.BASE_URL
		for i in range(len(batch_strings)):
			if i == 0:
				request_string += 'v1.1?q=' + batch_strings[i]
			else:
				request_string +=  '&q=' + batch_strings[i]
		
		result_dict = self.fetcher.get(request_string)
	
		# parse all url strings into real url objects
		# TODO: handle errors in url parsing
		parsed_dict = dict()
		for short_url_string in result_dict:
			parsed_dict[urlparse(short_url_string)] = urlparse(result_dict[short_url_string])
		
		return parsed_dict

	   
	
class LongURL(Service):
	
	def __init__(self, fetcher, priority = 0):
		
		Service.__init__(self, fetcher, priority = priority)
		
		self.BASE_URL = 'http://api.longurl.org/v2/'
		self.SHORTENER_LIST = self.load_service_list()

		
	def supports_shortener(self, domain):
		return domain in self.SHORTENER_LIST
	
	
	# load the list of shorteners that longurl.org api supports expanding
	def load_service_list(self):
		
		service_dict = self.fetcher.get(self.BASE_URL + 'services?format=json')
		return service_dict.keys()
	
	
	def expand(self, url):
		
		url_string = url.geturl()
		
		response_dict = self.fetcher.get(self.BASE_URL + 'expand?url=' + url_string + '&format=json&title=1')
			
		if response_dict.has_key('long-url'):
			return urlparse(response_dict['long-url'])
		else:
			raise ResolutionException("Could not resolve url: " + url_string)
			
