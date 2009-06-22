import StringIO
import logging
import unittest
import zeit.solr.testing
import zope.app.testing.xmlrpc
import zope.security.management


class XMLRPCTest(zeit.solr.testing.FunctionalTestCase):

    def setUp(self):
        super(XMLRPCTest, self).setUp()
        server = zope.app.testing.xmlrpc.ServerProxy(
            'http://solr:solrpw@localhost/')
        self.update_solr = getattr(server, '@@update_solr')
        # ServerProxy starts its own interactions
        zope.security.management.endInteraction()

        self.log = StringIO.StringIO()
        self.log_handler = logging.StreamHandler(self.log)
        logging.root.addHandler(self.log_handler)
        self.old_log_level = logging.root.level
        logging.root.setLevel(logging.INFO)

    def tearDown(self):
        logging.root.removeHandler(self.log_handler)
        logging.root.setLevel(self.old_log_level)
        super(XMLRPCTest, self).tearDown()

    def test_update_via_xmlrpc(self):
        self.update_solr('http://xml.zeit.de/online/2007/01/Somalia')
        self.assert_(self.solr.update_raw.called)
        xml = self.solr.update_raw.call_args[0][0]
        self.assertEqual('http://xml.zeit.de/online/2007/01/Somalia',
                         xml.xpath('//field[@name="uniqueId"]/text()')[0])
        self.assert_(
            "zope.solr triggered solr index update for "
            "'http://xml.zeit.de/online/2007/01/Somalia'"
            in self.log.getvalue())


def test_suite():
    return unittest.makeSuite(XMLRPCTest)
