import pkg_resources
import zope.app.testing.functional


SolrLayer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'SolrLayer', allow_teardown=True)
