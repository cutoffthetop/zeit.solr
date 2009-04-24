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

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.solr.interfaces.ISolrConverter)

    def __init__(self, context):
        self.context = context

    def prepare_dav_props(self):
        # This map contains three types:
        # interface, attribute, solr
        # TODO currently contains only a short preview list of types.
        solr_map = {
            (zeit.cms.content.interfaces.ICommonMetadata, "ressort")
                : "ressort",
            (zeit.cms.content.interfaces.ICommonMetadata, "sub_ressort")
                : "sub_ressort",
            (zeit.cms.content.interfaces.ICommonMetadata, "volume")
                : "volume",
            (zeit.cms.content.interfaces.ICommonMetadata, "title")
                : "title",
            (zeit.cms.content.interfaces.ICommonMetadata, "subtitle")
                : "subtitle",
            (zeit.content.image.interfaces.IImageMetadata, "caption")
                : "subtitle",
        }
        root_node = lxml.objectify.E.add()
        doc_node = lxml.objectify.E.doc()
        root_node.append(doc_node)
        for interface, att_name in solr_map:
            adapter = interface(self.context, None)
            attr = getattr(adapter, att_name, None)
            if attr is None:
                continue
            field_node = lxml.objectify.E.field(unicode(attr), name=att_name)
            doc_node.append(field_node)
        return root_node
