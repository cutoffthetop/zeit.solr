import lxml.html
import pysolr
import zeit.solr.interfaces
import zope.app.appsetup.product
import zope.interface


class SolrConnection(pysolr.Solr):

    zope.interface.implements(zeit.solr.interfaces.ISolr)

    def update_raw(self, xml):
        response = self._update(xml)
        if response.status != 200:
            raise pysolr.SolrError(self._extract_error(response))

    def _extract_error(self, response):
        # patched to use HTML instead of XML parser, so it does not choke
        # on <hr>-Tags, for example
        et = lxml.html.parse(response)
        return "[%s] %s" % (response.reason, et.findtext('body/h1'))


@zope.interface.implementer(zeit.solr.interfaces.ISolr)
def solr_connection_factory():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.solr')
    if config:
        url = config.get('solr-url')
    else:
        # XXX in tests there is no product config
        url = 'http://localhost:8180/solr'
    return SolrConnection(url)
