# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import BaseHTTPServer
import lxml.objectify
import pysolr
import random
import threading
import unittest
import zeit.solr.connection


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler, object):

    response_code = 200
    response_body = ''

    def do_POST(self):
        length = int(self.headers['content-length'])
        self.posts_received.append(dict(
            path=self.path,
            data=self.rfile.read(length),
            headers=self.headers,
        ))
        self.send_response(self.response_code)
        self.end_headers()
        self.wfile.write(self.response_body)

    def log_message(self, format, *args):
        # Silence logging
        pass


class TestSolrConnection(unittest.TestCase):

    def setUp(self):
        super(TestSolrConnection, self).setUp()
        self.port = random.randint(30000, 40000)
        self.solr = zeit.solr.connection.SolrConnection(
            'http://localhost:%s/solr/' % self.port)
        self.RequestHandler = type('TestRequestHandler', (RequestHandler,),
                                   {'posts_received': []})
        self.data = lxml.objectify.XML('<foo/>')

    def tearDown(self):
         self.httpd.shutdown()
         super(TestSolrConnection, self).tearDown()

    def start_httpd(self):
        self.thread = threading.Thread(target=self.start_httpd_handler)
        self.thread.start()

    def start_httpd_handler(self):
        self.running = True
        server_address = ('localhost', self.port)
        self.httpd = BaseHTTPServer.HTTPServer(server_address,
                                               self.RequestHandler)
        self.httpd.serve_forever(0.1)

    def test_update_raw(self):
        self.start_httpd()
        self.solr.update_raw(self.data)
        self.assertEquals(2, len(self.RequestHandler.posts_received))
        post = self.RequestHandler.posts_received
        self.assertEquals('/solr/update/', post[0]['path'])
        self.assertEquals("<?xml version='1.0' encoding='UTF-8'?>\n<foo/>",
                          post[0]['data'])
        self.assertEquals('text/xml', post[0]['headers']['Content-Type'])
        self.assertEquals('/solr/update/', post[1]['path'])
        self.assertEquals('<commit />', post[1]['data'])
        self.assertEquals('text/xml', post[1]['headers']['Content-Type'])

    def test_update_raw_with_error(self):
        self.RequestHandler.response_code = 500
        self.RequestHandler.response_body = (
            "<html><body><h1>Failed for some reason</h1> bla"
            "<hr></body></html>")
        self.start_httpd()
        try:
            self.solr.update_raw(self.data)
        except pysolr.SolrError, e:
            self.assertEquals(
                '[500 Internal Server Error] Failed for some reason',
                e.args[0])
        else:
            self.fail("Exception not raised")
        self.assertEquals(1, len(self.RequestHandler.posts_received))

    def test_update_raw_with_error_and_strange_html(self):
        self.RequestHandler.response_code = 500
        self.RequestHandler.response_body = "this is not html & broken"
        self.start_httpd()
        try:
            self.solr.update_raw(self.data)
        except pysolr.SolrError, e:
            self.assertEquals(
                '[500 Internal Server Error] this is not html & broken',
                e.args[0])
        else:
            self.fail("Exception not raised")
        self.assertEquals(1, len(self.RequestHandler.posts_received))
