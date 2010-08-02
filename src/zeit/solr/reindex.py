# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import xmlrpclib
import sys
import zeit.solr.connection


log = sys.stdout


class Reindex(object):

    def __init__(self, solr, solr_name, query, cms):
        self.solr = solr
        self.solr_name = solr_name
        self.query = query
        self.cms = cms

    def __call__(self):
        start = 0
        rows_per_batch = 100
        while True:
            result = self.solr.search(
                self.query, fl='id uniqueId', rows=rows_per_batch, start=start)
            print >>log, "Updating %s-%s of %s documents:" % (
                start, start+len(result), result.hits)
            start += rows_per_batch
            for doc in result:
                unique_id = doc['uniqueId']
                print >>log, "   %s" % unique_id.encode('utf8')
                try:
                    self.cms.update_solr(unique_id, self.solr_name)
                except xmlrpclib.Fault, e:
                    print >>log, 'Server returned fault while reindexing %s: %s' % (
                        unique_id, str(e))
            if start >= result.hits or not result:
                break


def reindex(solr_url, solr_name, cms_url):
    query = ' '.join(sys.argv[1:])
    if not query:
        print >>log, 'Usage: solr-reindex-query <solr-query>'
        return
    solr = zeit.solr.connection.SolrConnection(solr_url)
    cms = xmlrpclib.ServerProxy(cms_url)
    reindex = Reindex(solr, solr_name, query, cms)
    reindex()
