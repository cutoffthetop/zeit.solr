from optparse import OptionParser
from zeit.solr import query as lq
import gocept.async
import gocept.runner
import grokcore.component
import logging
import lxml.etree
import sys
import zeit.cms.interfaces
import zeit.cms.checkout.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zeit.solr.connection
import zeit.solr.interfaces
import zope.component
import zope.lifecycleevent


log = logging.getLogger(__name__)


@gocept.runner.once()
def update_main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-s", "--solr", dest="solr",
                      help="solr server uri")
    parser.add_option("-w", "--webdav", dest="webdav",
                      help="webdav server uri")
    parser.add_option("-p", "--published", action="store_true", dest="published",
                        help="only work on published resources")

    (options, args) = parser.parse_args()

    if not options.solr:
        parser.error("missing solr url")
    if not options.webdav:
        parser.error("missing webdav uri")
    if options.solr and options.webdav:
        zope.component.provideUtility(
            zeit.solr.connection.SolrConnection(options.solr))
        update_container(options.webdav, options.published)


def update_container(container_id, needs_publish):
    valid_status = ['OK', 'imported', 'importedVHB']
    conn = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    log.info("updating container '%s' on '%s'" % (container_id, conn.url))
    start_container = zeit.cms.interfaces.ICMSContent(container_id)
    stack = [start_container]
    while stack:
        content = stack.pop(0)
        if zeit.cms.repository.interfaces.ICollection.providedBy(content):
            stack.extend(content.values())
        if needs_publish == True:
            pubinfo = zeit.cms.workflow.interfaces.IPublishInfo(content)
            published = pubinfo.published
            status = zeit.workflow.interfaces.IOldCMSStatus(content).status
            if (published == False) and (status not in valid_status):
                continue
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

    def update(self, solr=u''):
        log.info("updating content '%s'" % self.context.uniqueId)
        conn = zope.component.getUtility(zeit.solr.interfaces.ISolr,
                                         name=solr)
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

    def update(self, solr=u''):
        # Note that we cannot use the UUID to delete because we just don't know
        # it. All we have is the uniqueId.
        conn = zope.component.getUtility(zeit.solr.interfaces.ISolr,
                                         name=solr)
        query = lq.field('uniqueId', self.context).encode('UTF-8')
        conn.delete(q=query, commit=True)


@zope.component.adapter(zeit.cms.workflow.interfaces.IPublishedEvent)
def update_public_after_publish(event):
    zeit.solr.interfaces.IUpdater(event.object).update(solr='public')


@zope.component.adapter(zeit.cms.workflow.interfaces.IBeforeRetractEvent)
def delete_public_after_retract(event):
    up = zope.component.getAdapter(
        event.object.uniqueId, zeit.solr.interfaces.IUpdater, name='delete')
    up.update(solr='public')



@grokcore.component.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zope.lifecycleevent.IObjectAddedEvent)
def index_after_add(context, event):
    if not zeit.cms.repository.interfaces.IRepository.providedBy(context):
        do_index_object(context)


@grokcore.component.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def index_after_checkin(context, event):
    # Only index if we're not already asynced. In the case a checkin happens in
    # an asynchronous task the indexinx via jabber invalidations is ver much
    # sufficient.
    if not gocept.async.is_async():
        do_index_object(context)


@gocept.async.function(u'events')
def do_index_object(context):
    zeit.solr.interfaces.IUpdater(context).update()
