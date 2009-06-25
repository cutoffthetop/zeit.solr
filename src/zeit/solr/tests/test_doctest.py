from zope.testing import doctest
import unittest
import zeit.cms.testing
import zeit.solr.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'converter.txt',
        package='zeit.solr',
        layer=zeit.solr.testing.SolrLayer,
        ))
    return suite
