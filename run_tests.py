import unittest

import tests.caching_test
import tests.services_test

if __name__ == '__main__':

	loader = unittest.TestLoader()

	suite = loader.loadTestsFromModule(tests.caching_test)
	suite.addTests( loader.loadTestsFromModule(tests.services_test) )

	unittest.TextTestRunner(verbosity = 2).run(suite)


