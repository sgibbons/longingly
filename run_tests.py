import unittest

import tests.caching_test

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(tests.caching_test.TestDefaultCache)

	unittest.TextTestRunner(verbosity = 2).run(suite)
