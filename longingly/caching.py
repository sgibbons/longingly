
class AbstractCache:

	def has_key(self, key):

		raise NotImplementedError()

	def get(self, key):

		raise NotImplementedError()

	def put(self, key, value):

		raise NotImplementedError()



class DefaultCache(AbstractCache):
	
	def __init__(self):
		
		self.store = dict()
		
	def has_key(self, key):
		
		return self.store.has_key(key)
	
	def get(self, key):
		
		return self.store[key]
	
	def put(self, key, value):
		
		self.store[key] = value
	
