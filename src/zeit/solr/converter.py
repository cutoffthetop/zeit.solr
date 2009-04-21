import zeit.connector.interfaces
import zeit.content.article
import zeit.solr.interfaces
import zope.component
import zope.interface


class SolrConverter(object):
    """Convert content objects to XML data using a Solr schema to feed the Solr
    server.

    """

    def __init__(self, context):
        self.context = context

    def prepare_dav_props(self):
        properties = zeit.connector.interfaces.IWebDAVProperties(self.context)


    zope.component.adapts(zeit.content.article.interfaces.IArticle)
    zope.interface.implements(zeit.solr.interfaces.ISolrConverter)
