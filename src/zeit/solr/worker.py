import gocept.runner
import logging
import lxml.etree
import sys
import zeit.cms.interfaces
import zeit.solr.connection
import zeit.solr.interfaces
import zope.component


logger = logging.getLogger(__name__)


@gocept.runner.once()
def update_main():
    if len(sys.argv) > 2:
        url = sys.argv[2]
        zope.component.provideUtility(zeit.solr.connection.SolrConnection(url))
    update_container(sys.argv[1])


def update_container(container_id):
    conn = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    logger.info("updating container '%s' on '%s'" % (container_id, conn.url))
    start_container = zeit.cms.interfaces.ICMSContent(container_id)
    stack = [start_container]
    while stack:
        content = stack.pop(0)
        if zeit.cms.repository.interfaces.ICollection.providedBy(content):
            stack.extend(content.values())
        update_worker(content)
    conn.commit()


def update_worker(content):
    logger.info("updating content '%s'" % content.uniqueId)
    assert zeit.cms.repository.interfaces.IRepositoryContent.providedBy(
        content)
    converter = zeit.solr.interfaces.ISolrConverter(content)
    try:
        root_node = converter.prepare_dav_props()
    except ValueError, e:
        print e
        return None
    update_pusher(root_node)


def update_pusher(root_node):
    conn = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    data = lxml.etree.tostring(root_node, pretty_print=True, encoding='utf8')
    # XXX it would be nicer to use add(), but then the converter would have to
    # be rewritten not to produce XML anymore (and pysolr would have to learn
    # how to set the boost), so we just push the raw XML here and bypass all
    # the pysolr niceties.
    conn.update_raw(data)
