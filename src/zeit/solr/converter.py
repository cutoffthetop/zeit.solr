import lxml.etree
import lxml.objectify
import zeit.connector.interfaces
import zeit.content.article
import zeit.solr.interfaces
import zeit.workflow.interfaces
import zope.component
import zope.interface


def join_tuple(tuple, solr_name, node):
    append_to_node(
        ' '.join(unicode(arg) for arg in tuple),
        solr_name,
        node
    )

def split_tuple(tuple, solr_name, node):
    for arg in tuple:
        append_to_node(unicode(arg), solr_name, node)

def join_labels(tuple, solr_name, node):
    append_to_node(
        ' '.join(unicode(arg.label) for arg in tuple),
        solr_name,
        node
    )

def canonize_date(arg, solr_name, node):
    solr_date = str(arg).replace(' ','T', 1)
    solr_date = solr_date.replace('+00:00', 'Z')
    append_to_node(unicode(solr_date), solr_name, node)

def get_type(properties, solr_name, node):
    type = properties.get(zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY)
    append_to_node(type, solr_name, node)

def append_to_node(value, solr_name, parent_node):
    child_node = lxml.objectify.E.field(value, name=solr_name)
    parent_node.append(child_node)


class SolrConverter(object):
    """Convert content objects to XML data using a Solr schema to feed the Solr
    server.

    """

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.solr.interfaces.ISolrConverter)

    # This map contains the following types:
    # interface, python attribute, solr attriute, filter function
    solr_mapping = [
        (
            zeit.cms.content.interfaces.ICommonMetadata,
            'authors',
            'authors',
            split_tuple,
        ),
        (
            zeit.cms.content.interfaces.ICommonMetadata,
            'authors',
            'authors_fulltext',
            join_tuple,
        ),
        (
            zeit.cms.content.interfaces.ICommonMetadata,
            'byline',
            'byline',
            append_to_node,
        ),
        (
            zeit.cms.workflow.interfaces.IModified,
            'date_last_modified',
            'date-last-modified',
            canonize_date,
        ),
        (
            zeit.cms.content.interfaces.ICommonMetadata,
            'shortTeaserTitle',
            'indexteaser_title',
            append_to_node,
        ),
        (
            zeit.cms.content.interfaces.ICommonMetadata,
            'shortTeaserText',
            'indexteaser_text',
            append_to_node,
        ),
        (
            zeit.cms.content.interfaces.ICommonMetadata,
            'keywords',
            'keywords',
            join_labels,
        ),
        (
            zeit.cms.workflow.interfaces.IModified,
            'last_modified_by',
            'last_modified_by',
            canonize_date,
        ),
        (
            zeit.cms.content.interfaces.ISemanticChange,
            'last_semantic_change',
            'last-semantic-change',
            canonize_date,
        ),
        (
            zeit.solr.interfaces.ISearchableText,
            'text',
            'main_text',
            append_to_node,
        ),
        (
            zeit.cms.content.interfaces.ICommonMetadata,
            'boxMostRead',
            'mostread',
            append_to_node,
        ),
        (
            zeit.cms.content.interfaces.ICommonMetadata,
            'page',
            'page',
            append_to_node,
        ),
        (
            zeit.cms.workflow.interfaces.IPublicationStatus,
            'published',
            'published',
            append_to_node,
        ),
        (
            zeit.workflow.interfaces.IContentWorkflow,
            'refined',
            'refined',
            append_to_node,
        ),
        (
            zeit.cms.content.interfaces.ICommonMetadata,
            'ressort',
            'ressort',
            append_to_node,
        ),
        (
            zeit.cms.content.interfaces.ICommonMetadata,
            'serie',
            'serie',
            append_to_node,
        ),
        (
            zeit.cms.content.interfaces.ICommonMetadata,
            'sub_ressort',
            'sub_ressort',
            append_to_node,
        ),
        (
            zeit.cms.content.interfaces.ICommonMetadata,
            'subtitle',
            'subtitle',
            append_to_node,
        ),
        (
            zeit.cms.content.interfaces.ICommonMetadata,
            'supertitle',
            'supertitle',
            append_to_node,
        ),
        (
            zeit.cms.content.interfaces.ICommonMetadata,
            'teaserTitle',
            'teaser_title',
            append_to_node,
        ),
        (
            zeit.cms.content.interfaces.ICommonMetadata,
            'teaserText',
            'teaser_text',
            append_to_node,
        ),
        (
            zeit.cms.content.interfaces.ICommonMetadata,
            'title',
            'title',
            append_to_node,
        ),
        (
            zeit.connector.interfaces.IWebDAVProperties,
            None,
            'type',
            get_type,
        ),
        (
            zeit.cms.content.interfaces.IUUID,
            'id',
            'uuid',
            append_to_node,
        ),
        (
            zeit.cms.content.interfaces.ICommonMetadata,
            'volume',
            'volume',
            append_to_node,
        ),
        (
            zeit.cms.interfaces.ICMSContent,
            'uniqueId',
            'uniqueId',
            append_to_node,
        ),
    ]

    def __init__(self, context):
        self.context = context
        self.adapters = {}

    def prepare_dav_props(self):
        root_node = lxml.objectify.E.add()
        doc_node = lxml.objectify.E.doc()
        root_node.append(doc_node)
        for (interface, att_name, solr_name, prepare) in self.solr_mapping:
            value = self.get_adapter(interface)
            if att_name is not None:
                value = getattr(value, att_name, None)
            if not value:
                continue
            prepare(value, solr_name, doc_node)
        return root_node

    def get_adapter(self, interface):
        try:
            adapter = self.adapters[interface]
        except KeyError:
            adapter = interface(self.context, None)
            self.adapters[interface] = adapter
        return adapter
