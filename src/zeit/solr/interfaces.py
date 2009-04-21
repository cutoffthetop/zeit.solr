import zope.interface


class ISolrConverter(zope.interface.Interface):
    """Converting XML files using a solr schema."""

    def to_solr_xml(tree):
        """Convert `tree` to solr valid XML"""
