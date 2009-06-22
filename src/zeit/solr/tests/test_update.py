from mock import Mock
import unittest
import zeit.cms.testing
import zeit.solr.interfaces
import zeit.solr.testing
import zope.component
import zope.interface


class UpdateTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.solr.testing.SolrLayer

    def setUp(self):
        super(UpdateTest, self).setUp()
        self.solr = Mock()
        zope.interface.alsoProvides(self.solr, zeit.solr.interfaces.ISolr)
        zope.component.provideUtility(self.solr)

    def tearDown(self):
        zope.component.getSiteManager().unregisterUtility(self.solr)
        super(UpdateTest, self).tearDown()

    def test_existing_id_should_be_updated(self):
        zeit.solr.interfaces.IUpdater(
            'http://xml.zeit.de/online/2007/01/Somalia').update()
        self.assert_(self.solr.update_raw.called)
        xml = self.solr.update_raw.call_args[0][0]
        self.assertEqual('http://xml.zeit.de/online/2007/01/Somalia',
                         xml.xpath('//field[@name="uniqueId"]/text()')[0])

    def test_nonexistent_id_should_be_deleted(self):
        zeit.solr.interfaces.IUpdater(
            'http://xml.zeit.de/nonexistent').update()
        self.assert_(self.solr.delete.called)
        query = self.solr.delete.call_args[1]['q']
        self.assert_('http://xml.zeit.de/nonexistent' in query)

    def test_malformed_id_is_treated_as_delete(self):
        zeit.solr.interfaces.IUpdater('foo').update()
        self.assert_(self.solr.delete.called)


def test_suite():
    return unittest.makeSuite(UpdateTest)
