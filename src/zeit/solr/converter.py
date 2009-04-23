import lxml.objectify
import lxml.etree
import zeit.connector.interfaces
import zeit.content.article
import zeit.solr.interfaces
import zope.component
import zope.interface


class SolrConverter(object):
    """Convert content objects to XML data using a Solr schema to feed the Solr
    server.

    """

    zope.component.adapts(zeit.content.article.interfaces.IArticle)
    zope.interface.implements(zeit.solr.interfaces.ISolrConverter)

    def __init__(self, context):
        self.context = context

    def prepare_dav_props(self):
        properties = zeit.connector.interfaces.IWebDAVProperties(self.context)

        root_node = lxml.objectify.E.add()
        doc_node = lxml.objectify.E.doc()
        root_node.append(doc_node)

        for prop_name, prop_ns in dict(properties):
            field_node = lxml.objectify.E.field(
                properties[prop_name, prop_ns],
                name=prop_name
            )
            doc_node.append(field_node)

        return root_node
