
class AbstractLogger:

	def __init__(self, log_level):

		self.log_level = log_level

	def log(self, message, severity):

		raise NotImplementedError()

	def debug(self, message):

		raise NotImplementedError()

	def info(self, message):

		raise NotImplementedError()

	def warn(self, message):

		raise NotImplementedError()

	def error(self, messsage):

		raise NotImplementedError()

	def fatal(self, message):
	
		raise NotImplementedError()




class DefaultLogger(AbstractLogger):

	def __init__(self, log_level = 2):
		
		AbstractLogger.__init__(self, log_level)

		self.DEBUG = 0
		self.INFO = 1
		self.WARN = 2
		self.ERROR = 3
		self.FATAL = 4

		self.NAME_MAP = {
			self.DEBUG: 'DEBUG',
			self.INFO: 'INFO',
			self.WARN: 'WARN',
			self.ERROR: 'ERROR',
			self.FATAL: 'FATAL'
		}
		
	def log(self, message, severity):
		
		# bound severity at FATAL
		severity = min(severity, self.FATAL)

		if severity >= self.log_level:
			print self.NAME_MAP[severity] + ': ' + message

	def debug(self, message):
		
		self.log(message, self.DEBUG)

	def info(self, message):

		self.log(message, self.INFO)

	def warn(self, message):

		self.log(message, self.WARN)

	def error(self, message):

		self.log(message, self.ERROR)

	def fatal(self, message):

		self.log(message, self.FATAL)
