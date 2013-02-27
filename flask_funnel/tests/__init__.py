import unittest

from flask_funnel.tests.test_funnel import FunnelTestCase


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FunnelTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
