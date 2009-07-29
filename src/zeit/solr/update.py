import gocept.runner
import logging
import lxml.etree
import sys
import zeit.cms.interfaces
import zeit.solr.connection
import zeit.solr.interfaces
import zope.component


log = logging.getLogger(__name__)


@gocept.runner.once()
def update_main():
    if len(sys.argv) > 2:
        url = sys.argv[2]
        zope.component.provideUtility(zeit.solr.connection.SolrConnection(url))
    update_container(sys.argv[1])


def update_container(container_id):
    conn = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    log.info("updating container '%s' on '%s'" % (container_id, conn.url))
    start_container = zeit.cms.interfaces.ICMSContent(container_id)
    stack = [start_container]
    while stack:
        content = stack.pop(0)
        if zeit.cms.repository.interfaces.ICollection.providedBy(content):
            stack.extend(content.values())
        zeit.solr.interfaces.IUpdater(content).update()
    conn.commit()


class IdUpdater(object):

    zope.component.adapts(basestring)
    zope.interface.implements(zeit.solr.interfaces.IUpdater)

    def __init__(self, context):
        self.context = context

    def update(self):
        try:
            content = zeit.cms.interfaces.ICMSContent(self.context)
            zeit.solr.interfaces.IUpdater(content).update()
        except TypeError: # id does not exist in repository
            zope.component.getAdapter(
                self.context,
                zeit.solr.interfaces.IUpdater, name='delete').update()


class ContentUpdater(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(zeit.solr.interfaces.IUpdater)

    def __init__(self, context):
        self.context = context

    def update(self):
        log.info("updating content '%s'" % self.context.uniqueId)
        conn = zope.component.getUtility(zeit.solr.interfaces.ISolr)
        converter = zeit.solr.interfaces.ISolrConverter(self.context)
        try:
            # XXX it would be nicer to use add(), but then the converter would
            # have to be rewritten not to produce XML anymore (and pysolr would
            # have to learn how to set the boost), so we just push the raw XML
            # here and bypass all the pysolr niceties.
            conn.update_raw(converter.convert())
        except zeit.solr.interfaces.SolrError, e:
            log.error("Solr server returned '%s' while updating %s" %
                         (e, self.context.uniqueId))
            return None


class Deleter(object):

    zope.component.adapts(basestring)
    zope.interface.implements(zeit.solr.interfaces.IUpdater)

    def __init__(self, context):
        self.context = context

    def update(self):
        conn = zope.component.getUtility(zeit.solr.interfaces.ISolr)
        conn.delete(q='uniqueId:%s' % self.context, commit=True)
