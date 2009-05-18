import unittest
import pkg_resources
import zeit.cms.testing
import zope.app.testing.functional
from zope.testing import doctest


SolrLayer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'SolrLayer', allow_teardown=True)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'converter.txt',
        'searchable.txt',
        layer=SolrLayer,
        optionflags=doctest.ELLIPSIS
        ))

    long_running = doctest.DocFileSuite(
        'handle.txt',
        optionflags=doctest.ELLIPSIS
        )
    long_running.level = 3
    suite.addTest(long_running)

    return suite
