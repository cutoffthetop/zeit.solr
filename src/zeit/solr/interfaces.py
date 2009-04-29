import zope.interface


class ISolrConverter(zope.interface.Interface):
    """Converting XML files using a solr schema."""

    def prepare_dav_props():
        """Prepare DAV properties for Solr"""


class ISearchableText(zope.interface.Interface):
    """Interface for handling text content of articles."""

