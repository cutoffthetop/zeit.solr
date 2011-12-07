# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import zeit.cms.testing
import zeit.solr.interfaces
import zope.app.testing.functional
import zope.component
import zope.interface


class RequestHandler(zeit.cms.testing.BaseHTTPRequestHandler):

    serve = []

    def do_GET(self):
        if self.serve:
            serve = self.serve.pop(0)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(serve)
        else:
            self.send_response(500)
            self.send_header('Reason', 'Nothing to serve for %s' % self.path)
            self.end_headers()


BaseHTTPLayer, port = zeit.cms.testing.HTTPServerLayer(RequestHandler)
SOLR_URL = 'http://localhost:%s/solr/' % port

product_config = """\
<product-config zeit.solr>
    solr-url %s
    public-solr-url http://dummy
</product-config>
""" % SOLR_URL


class HTTPLayer(BaseHTTPLayer):

    SOLR_URL = SOLR_URL
    REQUEST_HANDLER = RequestHandler

    @classmethod
    def testTearDown(cls):
        cls.REQUEST_HANDLER.serve[:] = []

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def setUp(cls):
        pass


BaseSolrLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)


class SolrLayer(HTTPLayer, BaseSolrLayer):

    @classmethod
    def testTearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def setUp(cls):
        pass


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
