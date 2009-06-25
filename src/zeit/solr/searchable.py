import zeit.cms.interfaces
import zeit.content.article.interfaces
import zeit.solr.interfaces
import zope.component
import zope.interface


class SearchableText(object):
    """Prepare articles and store the whole text content"""

    zope.component.adapts(zeit.content.article.interfaces.IArticle)
    zope.interface.implements(zeit.solr.interfaces.ISearchableText)

    def __init__(self, context):
        self.context = context
        main_text = []
        for p in self.context.xml.body.findall('p'):
            main_text.append(unicode(p))
        self.text = ''.join(main_text)
