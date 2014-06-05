# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.httpserverlayer.custom
import lxml.objectify
import pysolr
import socket
import time
import unittest
import zeit.solr.connection


class RequestHandler(gocept.httpserverlayer.custom.RequestHandler):

    response_code = 200
    response_body = ''
    reason = None
    posts_received = []
    sleep = 0

    def do_POST(self):
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


HTTP_LAYER = gocept.httpserverlayer.custom.Layer(
    RequestHandler, name='HTTPLayer', module=__name__)


class TestSolrConnection(unittest.TestCase):

    layer = HTTP_LAYER

    def setUp(self):
        super(TestSolrConnection, self).setUp()
        self.solr = zeit.solr.connection.SolrConnection(
            'http://%s/solr/' % self.layer['http_address'])
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

    def test_timeout_should_not_block_indefinitely(self):
        self.assertTrue(pysolr.TIMEOUTS_AVAILABLE)
        RequestHandler.sleep = 1
        self.solr.timeout = 0.5
        self.assertRaises(socket.timeout,
                          lambda: self.solr.update_raw(self.data))
        # httplib2 immediately retries a request upon a socket.error (while the
        # RequestHandler still sleeps). There is a race condition (which we
        # need a complicated diagram to explain) whether the second request is
        # handled by the server thread before or after the client raises
        # timeout. If the server handles the request *after* the client raises,
        # the test's tearDown might clear post_received and only then the
        # second POST is appended to the list, breaking test isolation. To
        # prevent this, wait for the second POST here before going into
        # tearDown.
        while len(RequestHandler.posts_received) < 2:
            time.sleep(0.01)
