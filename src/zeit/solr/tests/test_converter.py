# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest
import zeit.solr.testing


class TestGraphicalPreview(zeit.solr.testing.FunctionalTestCase):

    def setUp(self):
        import lxml.objectify
        import zeit.cms.interfaces
        import zeit.solr.converter
        super(TestGraphicalPreview, self).setUp()
        self.index = zeit.solr.converter.GraphicalPreview(
            'thumbnail', 'solr-thumbnail')
        self.image = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2006/DSC00109_2.JPG')
        self.xml = lxml.objectify.XML('<a/>')

    def test_url_for_image(self):
        self.index.process(self.image, self.xml)
        self.assertEquals('solr-thumbnail', self.xml.field.get('name'))
        self.assertEquals('/repository/2006/DSC00109_2.JPG/thumbnail',
                          self.xml.field)

    def test_no_url_for_testcontent(self):
        import zeit.cms.interfaces
        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        self.index.process(content, self.xml)
        self.assertEquals([], self.xml.getchildren())


class TestAccessCounter(unittest.TestCase):

    def setUp(self):
        import lxml.objectify
        import zeit.solr.converter
        self.index = zeit.solr.converter.AccessCounterIndex('nase')
        self.xml = lxml.objectify.XML('<a/>')

    def test_total_hits_should_not_include_todays_hits(self):
        ac = mock.Mock()
        ac.hits = 5
        ac.total_hits = 7
        self.index.process(ac, self.xml)
        self.assertEquals(2, self.xml.field)
        self.assertEquals('nase', self.xml.field.get('name'))

    def test_converter_should_index_access_count(self):
        from zeit.solr.converter import SolrConverter, AccessCounterIndex
        indexes = [index for index in SolrConverter.solr_mapping
                   if isinstance(index, AccessCounterIndex)]
        self.assertEquals(1, len(indexes))
