import lxml.etree
import lxml.objectify
import zeit.connector.interfaces
import zeit.content.article
import zeit.solr.interfaces
import zeit.workflow.interfaces
import zope.component
import zope.interface


def identity(arg):
    return arg

def join_tuple(tuple):
    if tuple:
        return ' '.join(unicode(arg) for arg in tuple)

def join_labels(tuple):
    if tuple:
        return ' '.join(unicode(arg.label) for arg in tuple)

def canonize_date(arg):
    if arg:
        solr_date = str(arg).replace(' ','T', 1)
        return solr_date.replace('+00:00', 'Z')


class SolrConverter(object):
    """Convert content objects to XML data using a Solr schema to feed the Solr
    server.

    """

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.solr.interfaces.ISolrConverter)

    def __init__(self, context):
        self.context = context

    def prepare_dav_props(self):
        # This map contains the following types:
        # interface, python attribute, solr attriute, filter function
        solr_map = {
            (zeit.cms.content.interfaces.ICommonMetadata, "authors")
                : ("authors", join_tuple),
            (zeit.cms.content.interfaces.ICommonMetadata, "byline")
                : ("byline", identity),
            (zeit.cms.workflow.interfaces.IModified, "date_last_modified")
                : ("date-last-modified", canonize_date),
            (zeit.cms.content.interfaces.ICommonMetadata, "shortTeaserText")
                : ("indexteaser_title", identity),
            (zeit.cms.content.interfaces.ICommonMetadata, "shortTeaserTitle")
                : ("indexteaser_text", identity),
            (zeit.cms.content.interfaces.ICommonMetadata, "keywords")
                : ("keywords", join_labels),
            (zeit.cms.workflow.interfaces.IModified, "last_modified_by")
                : ("last_modified_by", canonize_date),
            (zeit.cms.content.interfaces.ISemanticChange, "last_semantic_change")
                : ("last-semantic-change", canonize_date),
            (zeit.solr.interfaces.ISearchableText, "text")
                : ("main_text", identity),
            (zeit.cms.content.interfaces.ICommonMetadata, "boxMostRead")
                : ("mostread", identity),
            (zeit.cms.content.interfaces.ICommonMetadata, "page")
                : ("page", identity),
            (zeit.cms.workflow.interfaces.IPublishInfo, "published")
                : ("published", identity),
            (zeit.workflow.interfaces.IContentWorkflow, "refined")
                : ("refined", identity),
            (zeit.cms.content.interfaces.ICommonMetadata, "ressort")
                : ("ressort", identity),
            (zeit.cms.content.interfaces.ICommonMetadata, "serie")
                : ("serie", identity),
            (zeit.cms.content.interfaces.ICommonMetadata, "sub_ressort")
                : ("sub_ressort", identity),
            (zeit.cms.content.interfaces.ICommonMetadata, "subtitle")
                : ("subtitle", identity),
            (zeit.cms.content.interfaces.ICommonMetadata, "supertitle")
                : ("supertitle", identity),
            (zeit.cms.content.interfaces.ICommonMetadata, "teaserTitle")
                : ("teaser_title", identity),
            (zeit.cms.content.interfaces.ICommonMetadata, "teaserText")
                : ("teaser_text", identity),
            (zeit.cms.content.interfaces.ICommonMetadata, "title")
                : ("title", identity),
            (zeit.cms.repository.interfaces.IUnknownResource, "type")
                : ("type", identity),
            (zeit.cms.content.interfaces.IUUID, "id")
                : ("uuid", identity),
            (zeit.cms.content.interfaces.ICommonMetadata, "volume")
                : ("volume", identity),
            (zeit.cms.interfaces.ICMSContent, "uniqueId")
                : ("uniqueId", identity),
        }
        root_node = lxml.objectify.E.add()
        doc_node = lxml.objectify.E.doc()
        root_node.append(doc_node)
        for ((interface, att_name), (solr_name, prepare)) in solr_map.items():
            adapter = interface(self.context, None)
            attr = prepare(getattr(adapter, att_name, None))
            if att_name == 'uuid' and not attr:
                raise ValueError("Cannot index without UUID.")
            if not attr:
                continue
            field_node = lxml.objectify.E.field(
                attr,
                name=solr_name
            )
            doc_node.append(field_node)
        return root_node
