# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import transaction
import urllib2
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.solr.interfaces
import zope.component
import zope.event

# this is a 'zopectl run' script to correct the entries in the public solr
# that are marked not-published even though they actually are (#6428).


def fix_not_published(root):
    zope.site.hooks.setSite(root)
    fixer = NotPublishedFixer()
    solr = zope.component.getUtility(
        zeit.solr.interfaces.ISolr, name='public')

    start = 0
    rows = 50
    while True:
        results = solr.search('published:not-published',
                              sort='date-last-published desc',
                              start=start, rows=rows)
        if not results:
            break
        start += rows
        for item in results:
            fixer(item)
        # persist CMS changes of published status
        transaction.commit()


class NotPublishedFixer(object):

    def __call__(self, solr_item):
        uniqueId = solr_item['uniqueId']
        if not self.is_online(uniqueId):
            action = 'delete'
        else:
            action = 'update'
            self.mark_published(uniqueId, solr_item)
        print '%s: %s' % (action, uniqueId)
        zope.component.getAdapter(
            uniqueId, zeit.solr.interfaces.IUpdater, name=action).update(
            solr='public')

    def is_online(self, url):
        class HeadRequest(urllib2.Request):
            def get_method(self):
                return 'HEAD'
        try:
            urllib2.urlopen(HeadRequest(url))
            return True
        except urllib2.HTTPError:
            return False

    def mark_published(self, uniqueId, solr_item):
        zope.event.notify(
            zeit.connector.interfaces.ResourceInvalidatedEvent(uniqueId))
        try:
            content = zeit.cms.interfaces.ICMSContent(uniqueId)
        except TypeError:
            return
        else:
            pubinfo = zeit.cms.workflow.interfaces.IPublishInfo(content)
            if not pubinfo.published:
                date_last_published = solr_item['date-last-published']
                print 'publish: %s (%s)' % (uniqueId, date_last_published)
                pubinfo.published = True
