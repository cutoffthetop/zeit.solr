import zeit.cms.interfaces
import zeit.content.article.interfaces
import zope.component
import zope.index.text.interfaces
import zope.interface


class SearchableText(object):
    """Prepare articles and store the whole text content"""

    zope.component.adapts(zeit.content.article.interfaces.IArticle)
    zope.interface.implements(zope.index.text.interfaces.ISearchableText)

    def __init__(self, context):
        self.context = context

    def getSearchableText(self):
        main_text = []
        for p in self.context.xml.body.findall('p'):
            text = unicode(p).strip()
            if text:
                main_text.append(text)
        return main_text
