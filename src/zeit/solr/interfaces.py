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


class IUpdater(zope.interface.Interface):
    """Triggers an update of the solr index for an object.

    If the object exists in the repository, the solr index is updated,
    else the object is deleted from the solr index.
    """

    def update(solr=u''):
        """Update solr indicated by ``solr``."""


class IIndex(zope.interface.Interface):
    # XXX is this coupled rather tightly to the SolrConverter.convert()
    # implementation. We might want to refactor this so that an Index
    # is an adapter that directly adapts ICMSContent to an XML snippet
    # (or something like that).

    interface = zope.interface.Attribute(
        'The interface from which we want to retrieve our attribute.')

    attribute = zope.interface.Attribute(
        'The attribute we are interested in.')

    def process(value, node):
        """converts the ``value`` to XML and appends it to ``node``."""
