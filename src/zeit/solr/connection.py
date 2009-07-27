# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import hashlib
import lxml.etree
import lxml.html
import os.path
import pysolr
import urllib2
import zeit.solr.interfaces
import zope.app.appsetup.product
import zope.interface


class SolrConnection(pysolr.Solr):
    # XXX this class is untested

    zope.interface.implements(zeit.solr.interfaces.ISolr)

    def update_raw(self, xml):
        data = lxml.etree.tostring(xml, encoding='UTF-8', xml_declaration=True)
        path = '%s/update/' % self.path
        result = self._send_request(
            'POST', path, data, {'Content-type': 'text/xml;charset=UTF-8'})
        result = lxml.objectify.fromstring(result)
        status = result.get('status')
        if status != '0':
            raise pysolr.SolrError(status, result.text)

    def _extract_error(self, response):
        # patched to use HTML instead of XML parser, so it does not choke
        # on <hr>-Tags, for example
        et = lxml.html.parse(response)
        return "[%s] %s" % (response.reason, et.findtext('body/h1'))

    def _send_request(self, method, path, body=None, headers=None):
        """Override to use urllib2 instead of httplib directly for file urls.

        This is used for testing only.

        """
        if self.url.startswith('file://'):
            assert method == 'GET' and not headers
            additional_path = path[len(self.path):]
            local_path = '/'.join(
                (self.url[7:], hashlib.md5(additional_path).hexdigest()))
            if not os.path.exists(local_path):
                raise ValueError("Could not find %s while opening %s" % (
                    local_path, path))
            return open(local_path).read()

        return super(SolrConnection, self)._send_request(
            method, path, body, headers)


@zope.interface.implementer(zeit.solr.interfaces.ISolr)
def solr_connection_factory():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.solr')
    url = config.get('solr-url')
    return SolrConnection(url)
