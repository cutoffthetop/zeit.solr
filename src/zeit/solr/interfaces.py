import zope.interface


class ISolr(zope.interface.Interface):
    """Connection to a solr server. Wraps a pysolr.Solr object,
    see there for available methods not listed here."""

    def update_raw(xml):
        """post raw XML to the solr server"""


class ISolrConverter(zope.interface.Interface):
    """Converting XML files using a solr schema."""

    def prepare_dav_props():
        """Prepare DAV properties for Solr"""


class ISearchableText(zope.interface.Interface):
    """Interface for handling text content of articles."""

