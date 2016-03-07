import lxml.etree
import pysolr
import xml.sax.saxutils
import zeit.solr.interfaces
import zope.app.appsetup.product
import zope.interface


class SolrConnection(pysolr.Solr):

    zope.interface.implements(zeit.solr.interfaces.ISolr)

    def update_raw(self, xml):
        data = lxml.etree.tostring(xml, encoding='UTF-8', xml_declaration=True)
        result = self._send_request(
            'POST', 'update/', data, {'Content-type': 'text/xml'})
        return result

    def delete(self, id=None, q=None, commit=True, fromPending=True,
               fromCommitted=True):
        if q:
            q = xml.sax.saxutils.escape(q)
        return super(SolrConnection, self).delete(id, q, commit, fromPending,
                                                  fromCommitted)


@zope.interface.implementer(zeit.solr.interfaces.ISolr)
def solr_connection_factory():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.solr')
    url = config.get('solr-url')
    return SolrConnection(url)


@zope.interface.implementer(zeit.solr.interfaces.ISolr)
def second_solr_connection_factory():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.solr')
    url = config.get('second-solr-url')
    if url:
        return SolrConnection(url)
