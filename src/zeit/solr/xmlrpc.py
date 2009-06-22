import logging
import zeit.solr.interfaces
import zope.app.publisher.xmlrpc


logger = logging.getLogger(__name__)


class UpdateIndex(zope.app.publisher.xmlrpc.XMLRPCView):

    def update_solr(self, uniqueId):
        logger.info("%s triggered solr index update for '%s'" %
                    (self.request.principal.id, uniqueId))
        zeit.solr.interfaces.IUpdater(uniqueId).update()
