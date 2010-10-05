import json
from urlparse import urlparse
import logging
import copy
import re
from fetcher import DefaultFetcher

class Cache:
	
	def __init__(self):
		
		self.store = dict()
		
	def has_key(self, key):
		
		return self.store.has_key(key)
	
	def get(self, key):
		
		return self.store[key]
	
	def put(self, key, value):
		
		self.store[key] = value
	
	
class Service:
	
	def __init__(self, fetcher, priority = 0):
		
		self.SUPPORTS_BATCH = False
		self.MAX_BATCH_SIZE = 0
		self.PRIORITY = priority
		self.fetcher = fetcher()
		
		
	def expand(self, url_string):
		raise NotImplementedError()
	
	def batch_expand(self, url_strings):	
		raise NotImplementedError()
	
	def supports_shortener(self, domain):
		raise NotImplementedError()
	

class Bitly(Service):
	
	def __init__(self, fetcher, login, api_key, priority = 0):
		
		super(Bitly, self).__init__(self, priority)
		
		self.SUPPORTS_BATCH = True
		self.BASE_URL = 'http://api.bit.ly/v3/'
		
		
	def supports_shortener(self):
		
		# TODO: implement
		raise NotImplementedError()
	
	def expand(self, url):
		
		raise NotImplementedError()
		

class LongURLPlease(Service):
	
	def __init__(self, fetcher, priority = 0):
		
		super(LongURLPlease, self).__init__(self, fetcher, priority)
		
		self.SUPPORTS_BATCH = True
		self.BASE_URL = 'http://www.longurlplease.com/api/v1.1/'
		
		self.SUPPORTED_REGEX = self.load_supported_regex()
		
	
	# load the regex for shortener support from the longurlplease api
	def load_supported_regex(self):
		
		return re.compile(self.fetcher.get(self.BASE_URL + 'supported-services.json')['regex'])
	
		
	def supports_shortener(self, domain):
		
		return self.SUPPORTED_REGEX.match(domain) != None
			

	def expand(self, url):
		
		urlstring = url.geturl()
		
		result_dict = self.fetcher.get(self.BASE_URL + '?q=' + urlstring)

		if result_dict.has_key(urlstring):
			return urlparse(result_dict[urlstring])
		else:
			raise ResolutionException("Failed to resolve the given URL " + urlstring)
	
	
	def batch_expand(self, url, batch):
		
		# [Url] -> [String]
		batch_strings = map(lambda u: u.geturl(), batch)
		
		# construct request string
		request_string = self.BASE_URL
		for i in range(len(batch_strings)):
			if i == 0:
				request_string += '?q=' + batch_strings[i]
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
		
		super(LongURL, self).__init__(self, priority)
		
		self.SHORTENER_LIST = self.load_service_list()
		self.BASE_URL = 'http://api.longurl.org/v2/'
	
		
	def supports_shortener(self, domain):
		return domain in self.SHORTENER_LIST
	
	
	# load the list of shorteners that longurl.org api supports expanding
	def load_shortener_list(self):
		
		service_dict = self.fetcher.fetch(self.BASE_URL + 'services?format=json')
		return service_dict.keys()
	
	
	def expand(self, url):
		
		url_string = url.geturl()
		
		response_dict = self.fetcher.fetch(self.BASE_URL + 'expand?url=' + url_string + '&format=json&title=1')
			
		if response_dict.has_key('long-url'):
			return urlparse(response_dict['long-url'])
		else:
			raise ResolutionException("Could not resolve url: " + url_string)
			


class Expander:
	
	# Example construction:
	"""
	Expander( 
		services = {
			LongUrlPlease: { 
				'priority': 0 
			},
			Bitly: { 
				'priority': 1, 
				'login': 'foo', 
				'apikey': 'af745b9c91'
			}
		},
		cache = Cache,
		fetcher = DefaultFetcher
	)
	"""
	def __init__(self, services = {}, cache = Cache, fetcher = DefaultFetcher):
				
		# cache for known expansions
		self.cache = cache()
		
		# adjustments to make to service priorities when they succeed/fail
		self.FAILURE_PENALTY = 5
		self.SUCCESS_REWARD = 1
		
		# max number of failed expansions before giving up on a url
		self.MAX_FAILURES = 3
		
		# instantiate configured service list
		# [Class] -> [Service]
		self.services = map(lambda s: s(fetcher = fetcher, **services[s]), services.keys())
		
	
	# Url, Boolean -> Service
	def pick_service(self, url, prefer_batch = False):
		
		# sort service list by priority
		priorities = sorted(filter(lambda s: s.supports_shortener(url.netloc), self.services), key = lambda s: s.priority)
		
		# if no services support this url format, return None
		if len(priorities) == 0:
			return None
		
		if prefer_batch:
			batch_services = filter(lambda s: s.SUPPORTS_BATCH, priorities)
			if len(batch_services > 0):
				return batch_services[0]
		
		return priorities[0]
		
	
	# [Url], Int -> [ [Url] ]
	def make_batches(self, queue, batch_size):
		
		batches = []
		while len(queue) > 0:
			batch = []
			for i in range(batch_size):
				batch.append(queue.pop())
				if len(queue) == 0:
					break
			batches.append(batch)
			
		return batches


		
	# expand a list of short-urls, returning a list of (shorturl, longurl) pairs and a list of shorturls that couldn't be resolved
	# [String] -> [(Url, Url)], [Url]
	def batch_expand(self, url_strings):
		
		# lists to track completed expansions, failed expansions, and urls not supported by any expansion service
		complete_expansions = [] # [(Url, Url)]
		failed_expansions = [] # [Url]
		unsupported = [] # [Url]				

		# first check cache for local results
		for url_string in url_strings:
			if self.cache.has_key(url_string):
				complete_expansions.append( (urlparse(url_string), urlparse(self.cache.get(url_string))) )
		
		# remove already cached urls from the list to process
		uncached_url_strings = filter(lambda u: self.cache.has_key(u), url_strings)
		
		# parse all url strings into proper url objects
		# [String] -> [Url]
		urls = map(lambda u: urlparse(u), uncached_url_strings)
		
		# track failure counts in order to blacklist unexpandable urls after enough failures
		failure_counts = dict() # { Url : Int }
		
		# keep making attempts to resolve urls, continually reprioritizing services based on performance
		# until all urls have been resolved or they have exceeded the max resolution attempt count (MAX_FAILURES)
		while True:
			
			# if this is the first run through, try to expand everything
			# otherwise, try to expand the short-urls that failed last time, except for those that have exceeded MAX_FAILURES
			if len(failed_expansions) > 0:
				urls = filter(lambda u: not failure_counts.has_key(u) or failure_counts[u] < self.MAX_FAILURES, failed_expansions)
				failed_expansions = []
				
			# pick services to handle the expansion of each url
			# [Url] -> [ (Service, Url) ]
			services = map(lambda u: (self.pick_service(u, prefer_batch = True), u), urls)
			
			# break out url processing assigments into { Service : [Url] } queues 
			assignments = dict() # { Service : [Url] }
			for service, url in services:
				
				# if no service exists to expand this url, add it to the unsupported list and don't attempt to expand it
				if not service:
					unsupported.append(url)
					continue
					
				if assignments.has_key(service):
					assignments[service].append(url)
				else:
					assignments[service] = [url]
					
			# dispatch the expansion requests for each service
			for service in assignments.keys():
				
				# handle batch capable services
				if service.SUPPORTS_BATCH:
					
					# chop queue up into batches of the maximum supported size to minimize API calls
					batches = self.make_batches(assignments[service], service.MAX_BATCH_SIZE)
					for batch in batches:
						
						try:
							# [Url] -> { Url : Url }
							expansions = service.batch_expand(batch)
							
						# if any failure occurs during expansion: keep the URLs from this batch around for the next expansion attempt
						# also penalize the priority of this service to take into account this failure
						except ResolutionException:
							
							# remember failed url
							failed_expansions.extend(batch)
							
							# penalize service rating
							service.priority -= self.FAILURE_PENALTY
							
							# update failure counts for blacklisting urls as unresolvable
							for url in batch:
								if failure_counts.has_key(url):
									failure_counts[url] += 1
								else:
									failure_counts[url] = 1
									
							continue
						
						# if successful: cache the results and remember the short-url/long-url pairs for returning upon completion
						# also reward the priority of this service for this success
						for short_url in expansions.keys():
							self.cache.put(short_url.geturl(), expansions[short_url].geturl())
							complete_expansions.append(short_url, expansions[short_url])
						
						service.priority += self.SUCCESS_REWARD
				
				# handle services that require one-at-a-time url expansion (no batch support)
				else:
					for url in assignments[service]:
						
						try:
							expansion = service.expand(url)
							
						# if the url fails to expand remember this url for retrying on the next pass
						# also penalize the priority of the service used to account for this failure
						except ResolutionException:
							
							# remember failed url
							failed_expansions.append(url)
							
							# penalize service for failure
							service.priority -= self.FAILURE_PENALTY
							
							# track failure counts for blacklisting urls
							if failure_counts.has_key(url):
								failure_counts[url] += 1
							else:
								failure_counts[url] = 1
								
							continue
						
					# on successful expansion cache the result and add this url to the list of expanded urls to be returned upon completion
					# also reward the priority of the service used for this success
					self.cache.put(url.geturl(), expansion.geturl())
					complete_expansions.append( (url, expansion) )
					service.priority += self.SUCCESS_REWARD
			
			# if all urls have been successfully expanded, return the results
			if len(failed_expansions) == 0:
				
				# compute list of abandoned urls (urls with too many failed attempts at expansion)
				failures = failure_counts.keys()
				abandoned = filter(lambda f: failure_counts[f] >= self.MAX_FAILURES, failures)
				
				return complete_expansions, abandoned.extend(unsupported)
		
		
	def expand(self, url_string):
		
		# parse the url string to get a proper object and to get a clean url string for a cache key (whitespace stripped and such) 
		url = urlparse(url_string)
		clean_url = url.geturl() #TODO: rename, should be clean_url_string or something
		
		if self.cache.has_key(clean_url):
			return urlparse(self.cache.get(clean_url))
		
		else:
			
			# pick a service to expand this url, returning false if no supporting service could be found
			service = self.pick_service(url)
			if not service:
				return False
				
			expansion = None
			failure_count = 0
			while not expansion and failure_count < self.MAX_FAILURES:
				
				try:
					expansion = service.expand(url)
					self.cache.put(clean_url, expansion.geturl())
					
				except ResolutionException:
					service.priority -= self.FAILURE_PENALTY
					failure_count += 1
					
			if failure_count < self.MAX_FAILURES:
				service.priority += self.SUCCESS_REWARD
				
			return expansion

 
		   
class ResolutionException(Exception):
	
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return repr(self.value)		



