# coding: utf8
from __future__ import with_statement
import gocept.async.tests
import mock
import unittest
import zeit.cms.checkout.helper
import zeit.cms.interfaces
import zeit.cms.repository
import zeit.cms.testcontenttype.testcontenttype
import zeit.solr.testing
import zope.component
import zope.interface


class UpdateTest(zeit.solr.testing.MockedFunctionalTestCase):

    def assert_unique_id(self, unique_id):
        xml = self.solr.update_raw.call_args[0][0]
        self.assertEqual(unique_id,
                         xml.xpath('//field[@name="uniqueId"]/text()')[0])

    def test_existing_id_should_be_updated(self):
        zeit.solr.interfaces.IUpdater(
            'http://xml.zeit.de/online/2007/01/Somalia').update()
        self.assertTrue(self.solr.update_raw.called)
        self.assert_unique_id('http://xml.zeit.de/online/2007/01/Somalia')

    def test_nonexistent_id_should_be_deleted(self):
        zeit.solr.interfaces.IUpdater(
            'http://xml.zeit.de/nonexistent').update()
        self.assert_(self.solr.delete.called)
        query = self.solr.delete.call_args[1]
        self.assertEquals({'commit': True,
                           'q': 'uniqueId:(http\\://xml.zeit.de/nonexistent)'},
                          query)

    def test_malformed_id_is_treated_as_delete(self):
        zeit.solr.interfaces.IUpdater('foo').update()
        self.assert_(self.solr.delete.called)

    def test_delete_with_unicode(self):
        zeit.solr.interfaces.IUpdater(
            u'http://xml.zeit.de/nöd-däh').update()
        query = self.solr.delete.call_args[1]
        self.assertEquals(
            {'commit': True,
             'q': 'uniqueId:(http\\://xml.zeit.de/n\xc3\xb6d\\-d\xc3\xa4h)'},
            query)

    def test_update_on_create(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['t1'] = (
            zeit.cms.testcontenttype.testcontenttype.TestContentType())
        gocept.async.tests.process()
        self.assertTrue(self.solr.update_raw.called)
        self.assert_unique_id('http://xml.zeit.de/t1')

    def test_update_on_checkin(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        with zeit.cms.checkout.helper.checked_out(repository['testcontent']):
            pass
        gocept.async.tests.process()
        self.assertTrue(self.solr.update_raw.called)
        self.assert_unique_id('http://xml.zeit.de/testcontent')



class UpdatePublicTest(zeit.solr.testing.MockedFunctionalTestCase):

    product_config = {'zeit.content.article': {}}

    def setUp(self):
        super(UpdatePublicTest, self).setUp()
        self.public = mock.Mock()
        zope.interface.alsoProvides(self.public, zeit.solr.interfaces.ISolr)
        zope.component.provideUtility(self.public, name='public')
        self.article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')

    def tearDown(self):
        zope.component.getSiteManager().unregisterUtility(self.public, name='public')
        super(UpdatePublicTest, self).tearDown()

    def test_update_after_publish(self):
        zope.event.notify(
            zeit.cms.workflow.interfaces.PublishedEvent(self.article))
        self.assert_(not self.solr.update_raw.called)
        self.assert_(self.public.update_raw.called)
        xml = self.public.update_raw.call_args[0][0]
        self.assertEqual('http://xml.zeit.de/online/2007/01/Somalia',
                         xml.xpath('//field[@name="uniqueId"]/text()')[0])

    def test_delete_after_retract(self):
        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforeRetractEvent(self.article))
        self.assert_(not self.solr.delete.called)
        self.assert_(self.public.delete.called)
        query = self.public.delete.call_args[1]
        self.assertEquals({'commit': True,
                           'q': 'uniqueId:(http\\://xml.zeit.de/online/2007/01/Somalia)'},
                          query)
