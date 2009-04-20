import unittest
from zope.testing import doctest

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        # test_docs
        optionflags=doctest.ELLIPSIS
        ))

    return suite
