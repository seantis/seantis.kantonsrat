from five import grok

from seantis.kantonsrat.types import IOrganization
from seantis.kantonsrat.browser.base import BaseView


class OrganizationView(BaseView):

    permission = 'zope2.View'
    grok.require(permission)
    grok.context(IOrganization)
    grok.name('view')

    template = grok.PageTemplateFile('templates/organization.pt')

    def active_members(self):
        return self.context.memberships('active')

    def inactive_members(self):
        return self.context.memberships('inactive')
