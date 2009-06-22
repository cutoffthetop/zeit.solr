from mock import Mock
import pkg_resources
import zeit.cms.testing
import zeit.solr.interfaces
import zope.app.testing.functional
import zope.component
import zope.interface


SolrLayer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'SolrLayer', allow_teardown=True)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = SolrLayer

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        self.solr = Mock()
        zope.interface.alsoProvides(self.solr, zeit.solr.interfaces.ISolr)
        zope.component.provideUtility(self.solr)

    def tearDown(self):
        zope.component.getSiteManager().unregisterUtility(self.solr)
        super(FunctionalTestCase, self).tearDown()
