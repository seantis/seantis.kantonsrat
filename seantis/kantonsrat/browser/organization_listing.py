from five import grok
from zope.security import checkPermission

from Products.ATContentTypes.interface import IATFolder

from seantis.kantonsrat.types.organization import is_organization_visible
from seantis.kantonsrat.browser.base import BaseView


class Listing(BaseView):

    grok.context(IATFolder)
    grok.require('zope2.View')

    grok.name('organization_listing')

    template = grok.PageTemplateFile('templates/organization_listing.pt')

    def list_item(self, item):
        # show all for managers
        if checkPermission('cmf.ModifyPortalContent', self.context):
            return True

        return is_organization_visible(item)
