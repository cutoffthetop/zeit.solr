# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.interfaces
import zeit.solr.converter
import zeit.solr.testing
import lxml.objectify


class TestThumbnail(zeit.solr.testing.FunctionalTestCase):

    def setUp(self):
        super(TestThumbnail, self).setUp()
        self.index = zeit.solr.converter.Thumbnail('thumbnail')
        self.image = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2006/DSC00109_2.JPG')
        self.xml = lxml.objectify.XML('<a/>')

    def test_url_for_image(self):
        self.index.process(self.image, self.xml)
        self.assertEquals('thumbnail', self.xml.field.get('name'))
        self.assertEquals('/repository/2006/DSC00109_2.JPG/@@thumbnail',
                          self.xml.field)

    def test_no_url_for_testcontent(self):
        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        self.index.process(content, self.xml)
        self.assertEquals([], self.xml.getchildren())
