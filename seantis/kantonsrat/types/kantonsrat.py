from five import grok
from zope.interface import Interface

from plone import api
from plone.directives import form

from seantis.people.interfaces import ICompoundColumns
from seantis.people.types.base import PersonBase
from seantis.people.interfaces import IPerson


class IMember(form.Schema):
    form.model("kantonsrat.xml")


class Member(PersonBase):

    def get_organizations_filter(self, orgtype):
        catalog = api.portal.get_tool('portal_catalog')
        organizations = set(b.UID for b in catalog(organization_type=orgtype))

        return lambda uuid: uuid in organizations

    def organization_uuids_by_type(self, orgtype):
        return IPerson(self).organization_uuids(
            org_filter=self.get_organizations_filter(orgtype)
        )

    def organizations_by_type(self, orgtype):
        return IPerson(self).organizations(
            org_filter=self.get_organizations_filter(orgtype)
        )

    @property
    def parties(self):
        return self.organizations_by_type('party')

    @property
    def party_uuids(self):
        return self.organization_uuids_by_type('party')

    @property
    def comittees(self):
        return self.organizations_by_type('comittee')

    @property
    def comittee_uuids(self):
        return self.organization_uuids_by_type('comittee')

    @property
    def factions(self):
        return self.organizations_by_type('faction')

    @property
    def faction_uuids(self):
        return self.organization_uuids_by_type('faction')


class CompoundColumns(grok.Adapter):

    grok.name('kantonsrat-compound-columns')
    grok.provides(ICompoundColumns)
    grok.context(Interface)

    def get_compound_columns(self):
        return {
            'parties': 'party_uuids',
            'comittees': 'comittee_uuids',
            'factions': 'faction_uuids'
        }
