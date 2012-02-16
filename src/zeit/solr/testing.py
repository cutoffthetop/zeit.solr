# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import pkg_resources
import zeit.cms.testing
import zeit.solr.interfaces
import zope.component
import zope.interface


product_config = """\
<product-config zeit.solr>
    solr-url file://%s
    public-solr-url http://dummy
</product-config>
""" % pkg_resources.resource_filename(__name__, 'tests/data')


SolrLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)


class SolrMockLayerBase(object):

    @classmethod
    def setUp(cls):
        cls.solr = mock.Mock()
        zope.interface.alsoProvides(cls.solr, zeit.solr.interfaces.ISolr)
        zope.component.provideUtility(cls.solr)
        cls.public_solr = mock.Mock()
        zope.interface.alsoProvides(
            cls.public_solr, zeit.solr.interfaces.ISolr)
        zope.component.provideUtility(cls.public_solr, name='public')

    @classmethod
    def tearDown(cls):
        zope.component.getSiteManager().unregisterUtility(cls.solr)
        zope.component.getSiteManager().unregisterUtility(cls.public_solr,
                                                          name='public')

    @classmethod
    def testTearDown(cls):
        cls.solr.reset_mock()
        cls.public_solr.reset_mock()


class SolrMockLayer(SolrLayer, SolrMockLayerBase):
    """Mocked solr."""


class MockedFunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = SolrMockLayer

    def setUp(self):
        super(MockedFunctionalTestCase, self).setUp()
        self.solr = self.layer.solr


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = SolrLayer

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        self.solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
