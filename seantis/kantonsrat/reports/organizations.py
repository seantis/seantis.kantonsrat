from plone import api
from seantis.kantonsrat import _
from .base import Report


class OrganizationsReport(Report):

    def populate(self):

        self.pdf.h1(self.context.title)

        self.pdf.h2(_(u'Content'))
        self.pdf.table_of_contents()
        self.pdf.pagebreak()

        for organization in (o.getObject() for o in self.get_organizations()):
            self.pdf.h1(organization.title)
            self.pdf.p(organization.description)

    def get_organizations(self):
        catalog = api.portal.get_tool('portal_catalog')
        return catalog(
            path={'query': '/'.join(self.context.getPhysicalPath())},
            portal_type='seantis.kantonsrat.organization'
        )

    def get_memberships(self, organization):
        catalog = api.portal.get_tool('portal_catalog')
        return catalog(
            path={'query': '/'.join(organization.getPhysicalPath())},
            portal_type='seantis.kantonsrat.membership'
        )
