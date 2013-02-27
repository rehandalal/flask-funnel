import unittest

from flask_funnel.tests.test_funnel import FunnelTestCase
from flask_funnel.tests.test_manager import ManagerTestCase


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FunnelTestCase))
    suite.addTest(unittest.makeSuite(ManagerTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
