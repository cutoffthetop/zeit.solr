# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import zeit.solr.testing


class QueryTest(zeit.solr.testing.FunctionalTestCase):

    def test_file_urls_map_to_md5(self):
        result = self.solr.search('obama')
        self.assertEquals(45, result.hits)
        self.assertEquals(2009, result.docs[0]['year'])
        self.assertEquals(
            'http://xml.zeit.de/online/2009/19/obama-deutschlandbesuch',
            result.docs[0]['uniqueId'])

    def test_not_existing(self):
        self.assertRaises(ValueError, self.solr.search, 'foo')


def test_suite():
    return unittest.makeSuite(QueryTest)
