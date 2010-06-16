# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import StringIO
import mock
import pkg_resources
import sys
import unittest
import xmlrpclib
import zeit.cms.testing
import zeit.solr.connection
import zeit.solr.reindex


# The figures are quite strange as the json we provide is quite strange ;)
query_result = """\
Updating 0-10 of 112 documents:
   http://xml.zeit.de/online/2009/25/jemen-entfuehrung-3
   http://xml.zeit.de/online/2009/26/bundeswehr-afghanistan-2
   http://xml.zeit.de/online/2009/26/cdu-wahlprogramm
   http://xml.zeit.de/online/2009/26/charite-kinderpornografie
   http://xml.zeit.de/online/2009/26/das-lebendige-wort-gottes
   http://xml.zeit.de/online/2009/26/erde-sd-kuehlmittel
   http://xml.zeit.de/online/2009/26/erde-sd-wattenmeer
   http://xml.zeit.de/online/2009/26/erde-sd-windanlagen
   http://xml.zeit.de/online/2009/26/ganz-praktisch
   http://xml.zeit.de/online/2009/26/gfk-index
Updating 100-110 of 112 documents:
   http://xml.zeit.de/online/2009/25/jemen-entfuehrung-3
   http://xml.zeit.de/online/2009/26/bundeswehr-afghanistan-2
   http://xml.zeit.de/online/2009/26/cdu-wahlprogramm
   http://xml.zeit.de/online/2009/26/charite-kinderpornografie
   http://xml.zeit.de/online/2009/26/das-lebendige-wort-gottes
   http://xml.zeit.de/online/2009/26/erde-sd-kuehlmittel
   http://xml.zeit.de/online/2009/26/erde-sd-wattenmeer
   http://xml.zeit.de/online/2009/26/erde-sd-windanlagen
   http://xml.zeit.de/online/2009/26/ganz-praktisch
   http://xml.zeit.de/online/2009/26/gfk-index
"""


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


HTTPLayer, port = zeit.cms.testing.HTTPServerLayer(RequestHandler)
SOLR_URL = 'http://localhost:%s/solr/' % port


class TestReindex(unittest.TestCase):

    layer = HTTPLayer

    def setUp(self):
        super(TestReindex, self).setUp()
        self.orig_xmlrpc_proxy = xmlrpclib.ServerProxy
        self.xmlrpc_instance = mock.Mock()
        xmlrpclib.ServerProxy = mock.Mock()
        xmlrpclib.ServerProxy.return_value = self.xmlrpc_instance
        self.log = StringIO.StringIO()
        self.old_log = zeit.solr.reindex.log
        zeit.solr.reindex.log = self.log
        self.cms_url = 'http://localhost/'
        self.argv = sys.argv
        sys.argv = [sys.argv[0]]

    def tearDown(self):
        xmlrpclib.ServerProxy = self.orig_xmlrpc_proxy
        zeit.solr.reindex.log = self.old_log
        output = self.log.getvalue()
        sys.argv = self.argv
        RequestHandler.serve[:] = []
        super(TestReindex, self).tearDown()

    def test_query(self):
        self.expected = query_result
        xmlrpc = mock.Mock()
        query = 'boost:[2 TO *]'
        solr = zeit.solr.connection.SolrConnection(SOLR_URL)
        RequestHandler.serve.append(pkg_resources.resource_string(
                __name__, 'data/test_reindex.test_query.boost-test.json'))
        RequestHandler.serve.append(pkg_resources.resource_string(
                __name__, 'data/test_reindex.test_query.boost-test.2.json'))
        reindex = zeit.solr.reindex.Reindex(solr, 'public', query, xmlrpc)
        reindex()
        self.assertTrue(xmlrpc.update_solr.called)
        self.assertEquals(20, len(xmlrpc.update_solr.call_args_list))
        self.assertEquals(query_result, self.log.getvalue())

    def test_entrypoint_without_query(self):
        zeit.solr.reindex.reindex(SOLR_URL, 'public', self.cms_url)
        self.assertEquals('Usage: solr-reindex-query <solr-query>\n',
                          self.log.getvalue())

    def test_entrypoint_with_query(self):
        sys.argv.extend(['merkel', 'steinmeier', 'obama'])
        RequestHandler.serve.append(pkg_resources.resource_string(
            __name__, 'data/test_reindex.test_entrypoint_with_query.json'))
        zeit.solr.reindex.reindex(SOLR_URL, 'public', self.cms_url)
        self.assertTrue(xmlrpclib.ServerProxy.called)
        self.assertTrue(self.xmlrpc_instance.update_solr.called)
        self.assertEquals(
            'http://xml.zeit.de/online/2009/04/obama-merkel-amtseinfuehrung',
            self.xmlrpc_instance.update_solr.call_args_list[0][0][0])
        self.assertEquals(
            'public',
            self.xmlrpc_instance.update_solr.call_args_list[0][0][1])

    def test_xmlrpc_fault_continues_reindexing_remaining_objects(self):
        xmlrpc = mock.Mock()
        def raiser(*args, **kw):
            raise xmlrpclib.Fault(100, 'error')
        xmlrpc.update_solr.side_effect = raiser
        query = 'boost:[2 TO *]'
        solr = zeit.solr.connection.SolrConnection(SOLR_URL)
        RequestHandler.serve.append(pkg_resources.resource_string(
                __name__, 'data/test_reindex.test_query.boost-test.json'))
        RequestHandler.serve.append(pkg_resources.resource_string(
                __name__, 'data/test_reindex.test_query.boost-test.2.json'))
        reindex = zeit.solr.reindex.Reindex(solr, 'public', query, xmlrpc)
        reindex()
        self.assertTrue(xmlrpc.update_solr.called)
        self.assertEquals(20, len(xmlrpc.update_solr.call_args_list))
