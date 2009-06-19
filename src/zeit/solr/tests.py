from zope.testing import doctest
import pkg_resources
import unittest
import zeit.cms.testing
import zope.app.testing.functional


SolrLayer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'SolrLayer', allow_teardown=True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'converter.txt',
        'searchable.txt',
        layer=SolrLayer,
        ))
    return suite
