import zeit.solr.interfaces
import zope.component
import zope.interface


class SolrConverter(object):
    """Convert content objects to XML data using a Solr schema to feed the Solr
    server.

    """

    zope.component.adapts(zope.interface.Interface)
    zope.interface.implements(zeit.solr.interfaces.ISolrConverter)
