# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import BaseHTTPServer
import lxml.objectify
import pysolr
import random
import threading
import unittest
import zeit.cms.testing
import zeit.solr.connection


class RequestHandler(zeit.cms.testing.BaseHTTPRequestHandler):

    response_code = 200
    response_body = ''
    reason = None
    posts_received = []
    sleep = 0

    def do_POST(self):
        import socket
        import time
        length = int(self.headers['content-length'])
        self.posts_received.append(dict(
            path=self.path,
            data=self.rfile.read(length),
            headers=self.headers,
        ))
        time.sleep(self.sleep)
        self.send_response(self.response_code)
        if self.reason:
            self.send_header('Reason', self.reason)
        self.end_headers()
        self.wfile.write(self.response_body)


HTTPLayer, port = zeit.cms.testing.HTTPServerLayer(RequestHandler)


class TestSolrConnection(unittest.TestCase):

    layer = HTTPLayer

    def setUp(self):
        super(TestSolrConnection, self).setUp()
        self.solr = zeit.solr.connection.SolrConnection(
            'http://localhost:%s/solr/' % port)
        self.data = lxml.objectify.XML('<foo/>')

    def tearDown(self):
        RequestHandler.posts_received[:] = []
        RequestHandler.response_code = 200
        RequestHandler.response_body = ''
        RequestHandler.reason = None
        RequestHandler.sleep = 0
        super(TestSolrConnection, self).tearDown()

    def test_update_raw(self):
        self.solr.update_raw(self.data)
        self.assertEquals(1, len(RequestHandler.posts_received))
        post = RequestHandler.posts_received
        self.assertEquals('/solr/update/', post[0]['path'])
        self.assertEquals("<?xml version='1.0' encoding='UTF-8'?>\n<foo/>",
                          post[0]['data'])
        self.assertEquals('text/xml', post[0]['headers']['Content-Type'])

    def test_update_raw_with_error(self):
        RequestHandler.response_code = 500
        RequestHandler.response_body = (
            "<html><body><h1>Failed for some reason</h1> bla"
            "<hr></body></html>")
        RequestHandler.reason = 'Failed for a reason'
        try:
            self.solr.update_raw(self.data)
        except pysolr.SolrError, e:
            self.assertEquals(
                '[Reason: Failed for a reason]\n<html><body><h1>'
                'Failed for some reason</h1> bla<hr></body></html>',
                e.args[0])
        else:
            self.fail("Exception not raised")
        self.assertEquals(1, len(RequestHandler.posts_received))

    def test_update_raw_with_error_and_strange_html(self):
        RequestHandler.response_code = 500
        RequestHandler.response_body = "this is not html & broken"
        try:
            self.solr.update_raw(self.data)
        except pysolr.SolrError, e:
            self.assertEquals(
                '[Reason: None]\nthis is not html & broken',
                e.args[0])
        else:
            self.fail("Exception not raised")
        self.assertEquals(1, len(RequestHandler.posts_received))

    def test_delete_escapes_xml(self):
        self.solr.delete(q='foo:a\\&b', commit=False)
        self.assertEquals(1, len(RequestHandler.posts_received))
        post = RequestHandler.posts_received
        self.assertEquals(
            '<delete><query>foo:a\\&amp;b</query></delete>',
            post[0]['data'])

    def test_timeout_should_not_block_indefinately(self):
        import time
        self.assertTrue(pysolr.TIMEOUTS_AVAILABLE)
        RequestHandler.sleep = 1
        self.solr.timeout = 0.5
        import socket
        self.assertRaises(socket.timeout,
                          lambda: self.solr.update_raw(self.data))
