# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import StringIO
import mock
import pkg_resources
import random
import sys
import unittest
import xmlrpclib
import zeit.solr.connection
import zeit.solr.reindex


testdata = 'file://%s' % pkg_resources.resource_filename(__name__, 'data')

query_result = """\
Updating 10 of 1382 documents:
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

class TestReindex(unittest.TestCase):

    def setUp(self):
        super(TestReindex, self).setUp()
        self.orig_xmlrpc_proxy = xmlrpclib.ServerProxy
        self.xmlrpc_instance = mock.Mock()
        xmlrpclib.ServerProxy = mock.Mock()
        xmlrpclib.ServerProxy.return_value = self.xmlrpc_instance
        self.log = StringIO.StringIO()
        self.old_log = zeit.solr.reindex.log
        zeit.solr.reindex.log = self.log
        self.cms_url = 'http://localhost:%s/' % random.randint(30000, 40000)
        self.argv = sys.argv
        sys.argv = [sys.argv[0]]

    def tearDown(self):
        xmlrpclib.ServerProxy = self.orig_xmlrpc_proxy
        zeit.solr.reindex.log = self.old_log
        output = self.log.getvalue()
        sys.argv = self.argv
        super(TestReindex, self).tearDown()

    def test_query(self):
        self.expected = query_result
        xmlrpc = mock.Mock()
        query = 'boost:[2 TO *]'
        solr = zeit.solr.connection.SolrConnection(testdata)
        reindex = zeit.solr.reindex.Reindex(solr, 'public', query, xmlrpc)
        reindex()
        self.assertTrue(xmlrpc.update_solr.called)
        self.assertEquals(10, len(xmlrpc.update_solr.call_args_list))
        self.assertEquals(query_result, self.log.getvalue())

    def test_entrypoint_without_query(self):
        zeit.solr.reindex.reindex(testdata, 'public', self.cms_url)
        self.assertEquals('Usage: solr-reindex-query <solr-query>\n',
                          self.log.getvalue())

    def test_entrypoint_with_query(self):
        sys.argv.extend(['merkel', 'steinmeier', 'obama'])
        zeit.solr.reindex.reindex(testdata, 'public', self.cms_url)
        self.assertTrue(xmlrpclib.ServerProxy.called)
        self.assertTrue(self.xmlrpc_instance.update_solr.called)
        self.assertEquals(
            'http://xml.zeit.de/online/2009/04/obama-merkel-amtseinfuehrung',
            self.xmlrpc_instance.update_solr.call_args_list[0][0][0])
        self.assertEquals(
            'public',
            self.xmlrpc_instance.update_solr.call_args_list[0][0][1])
