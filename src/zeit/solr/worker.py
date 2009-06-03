import gocept.runner
import lxml.etree
import sys
import zeit.cms.interfaces
import zeit.solr.handle
import zeit.solr.interfaces
import zope.app.security.interfaces


@gocept.runner.once()
def update_main():
    update_container(sys.argv[1])


def update_container(container_id):
    start_container = zeit.cms.interfaces.ICMSContent(container_id)
    stack = [start_container]
    while stack:
        content = stack.pop(0)
        if zeit.cms.repository.interfaces.ICollection.providedBy(content):
            stack.extend(content.values())
        update_worker(content)
    commit = lxml.objectify.E.commit()
    update_pusher(commit)


def update_worker(content):
    print content.uniqueId
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
    data = lxml.etree.tostring(root_node, pretty_print=True, encoding='utf8')
    solrh = zeit.solr.handle.SolrHandle()
    solrh.url = '194.77.156.97:8180'
    solrh.push_data(data)

