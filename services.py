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
		
		
	def supports_shortener(self):
		
		# TODO: implement
		raise NotImplementedError()
	
	def expand(self, url):
		
		raise NotImplementedError()


	def batch_expand(self, url):

		raise NotImplementedError()
		

class LongURLPlease(Service):
	
	def __init__(self, fetcher, priority = 0):
		
		Service.__init__(self, fetcher, priority = priority)
		
		self.SUPPORTS_BATCH = True
		self.BASE_URL = 'http://www.longurlplease.com/api/'
		
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
			
