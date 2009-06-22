# export this here so clients are not coupled to pysolr
from pysolr import SolrError
import zope.interface


class ISolr(zope.interface.Interface):
    """Connection to a solr server. Wraps a pysolr.Solr object,
    see there for available methods not listed here."""

    def update_raw(xml):
        """post raw XML (given as an lxml.etree node) to the solr server"""


class ISolrConverter(zope.interface.Interface):
    """Converting XML files using a solr schema."""

    def convert():
        """Prepare DAV properties for Solr"""


class ISearchableText(zope.interface.Interface):
    """Interface for handling text content of articles."""

