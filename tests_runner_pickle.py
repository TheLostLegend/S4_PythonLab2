import unittest
import pickle_tests
import sys
import os

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(pickle_tests)
    sys.stdout = open(os.devnull, 'w')
    unittest.TextTestRunner(verbosity=2).run(suite)
    sys.stdout = sys.__stdout__
