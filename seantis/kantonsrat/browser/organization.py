from five import grok

from plone.uuid.interfaces import IUUID
from zope.component import queryUtility

from seantis.kantonsrat.interfaces import IMotionsProvider
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

    def future_members(self):
        return self.context.memberships('future')

    def submitted_motions(self):
        motions_provider = queryUtility(IMotionsProvider)
        if motions_provider:
            return motions_provider.motions_by_entity(IUUID(self.context))
        else:
            return []
