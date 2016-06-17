import logging
import lxml.etree
import pysolr
import xml.sax.saxutils
import zeit.solr.interfaces
import zope.app.appsetup.product
import zope.interface


log = logging.getLogger(__name__)


class SolrConnection(pysolr.Solr):

    zope.interface.implements(zeit.solr.interfaces.ISolr)

    ignore_search_errors = False

    def search(self, *args, **kw):
        try:
            return super(SolrConnection, self).search(*args, **kw)
        except pysolr.SolrError, e:
            if self.ignore_search_errors:
                log.warn(str(e))
                return pysolr.Results(docs=(), hits=0)
            else:
                raise

    def update_raw(self, xml):
        data = lxml.etree.tostring(xml, encoding='UTF-8', xml_declaration=True)
        result = self._send_request(
            'POST', 'update/', data, {'Content-type': 'text/xml'})
        return result

    def delete(self, id=None, q=None, **kw):
        if q:
            # patched
            q = xml.sax.saxutils.escape(q)
        if id is None and q is None:
            raise ValueError('You must specify "id" or "q".')
        elif id is not None and q is not None:
            raise ValueError('You many only specify "id" OR "q", not both.')
        elif id is not None:
            m = '<delete><id>%s</id></delete>' % id
        elif q is not None:
            # patched to use unicode
            m = u'<delete><query>%s</query></delete>' % q

        return self._update(m, **kw)


@zope.interface.implementer(zeit.solr.interfaces.ISolr)
def solr_connection_factory():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.solr')
    url = config.get('solr-url')
    result = SolrConnection(url)
    if config.get('solr-ignore-search-errors'):
        result.ignore_search_errors = True
    return result


@zope.interface.implementer(zeit.solr.interfaces.ISolr)
def second_solr_connection_factory():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.solr')
    url = config.get('second-solr-url')
    if url:
        return SolrConnection(url)
