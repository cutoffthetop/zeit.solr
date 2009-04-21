import unittest
import os
import zeit.cms.testing
import zope.app.testing.functional
from zope.testing import doctest


ArticleLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'ArticleLayer', allow_teardown=True)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'converter.txt',
        layer=ArticleLayer,
        optionflags=doctest.ELLIPSIS
        ))

    return suite
