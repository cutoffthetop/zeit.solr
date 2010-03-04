# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import xmlrpclib
import optparse
import sys
import zeit.solr.connection


log = sys.stdout


class Reindex(object):

    def __init__(self, solr, query, cms):
        self.solr = solr
        self.query = query
        self.cms = cms

    def __call__(self):
        result = self.solr.search(
            self.query, fl='id uniqueId', rows=10000)
        print >>log, "Updating %s of %s documents:" % (len(result), result.hits)
        for doc in result:
            unique_id = doc['uniqueId']
            print >>log, "   %s" % unique_id
            self.cms.update_solr(unique_id)


def reindex(solr_url, cms_url):
    query = ' '.join(sys.argv[1:])
    if not query:
        print >>log, 'Usage: solr-reindex-query <solr-query>'
        return
    solr = zeit.solr.connection.SolrConnection(solr_url)
    cms = xmlrpclib.ServerProxy(cms_url)
    reindex = Reindex(solr, query, cms)
    reindex()
