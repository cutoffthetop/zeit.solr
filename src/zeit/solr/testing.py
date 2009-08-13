# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import pkg_resources
import zeit.cms.testing
import zeit.solr.interfaces
import zope.app.testing.functional
import zope.component
import zope.interface


product_config = """\
<product-config zeit.solr>
    solr-url file://%s
    public-solr-url http://dummy
</product-config>
""" % pkg_resources.resource_filename(__name__, 'tests/data')

SolrLayer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'SolrLayer', allow_teardown=True,
    product_config=product_config)


class MockedFunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = SolrLayer

    def setUp(self):
        super(MockedFunctionalTestCase, self).setUp()
        self.solr = mock.Mock()
        zope.interface.alsoProvides(self.solr, zeit.solr.interfaces.ISolr)
        zope.component.provideUtility(self.solr)

    def tearDown(self):
        zope.component.getSiteManager().unregisterUtility(self.solr)
        super(MockedFunctionalTestCase, self).tearDown()


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = SolrLayer

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        self.solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
