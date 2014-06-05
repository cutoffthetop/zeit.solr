from zope.testing import doctest
import unittest
import zeit.cms.testing
import zeit.solr.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'converter.txt',
        package='zeit.solr',
        layer=zeit.solr.testing.ZCML_LAYER,
    ))
    suite.addTest(doctest.DocFileSuite(
        'query.txt',
        package='zeit.solr',
    ))
    return suite
