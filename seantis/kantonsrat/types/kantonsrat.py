import logging
log = logging.getLogger('seantis.kantonsrat')

from five import grok
from zope.interface import Interface
from zope.component import queryUtility

from plone import api
from plone.directives import form
from plone.uuid.interfaces import IUUID

from seantis.people.interfaces import ICompoundColumns
from seantis.people.types.base import PersonBase
from seantis.people.interfaces import IPerson
from seantis.people.utils import LinkList

from seantis.kantonsrat import _
from seantis.kantonsrat.interfaces import IMotionsProvider


class IMember(form.Schema):
    form.model("kantonsrat.xml")


class Member(PersonBase):

    custom_titles = {
        'motions': _(u'Submitted Motions')
    }

    @property
    def membership_fields(self):
        parent_fields = super(Member, self).membership_fields
        parent_fields.update({
            'party_memberships': _(u'Party'),
            'faction_memberships': _(u'Factions'),
            'committee_memberships': _(u'Committees')
        })

        return parent_fields

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

    def memberships_by_type(self, orgtype):
        return IPerson(self).memberships(
            org_filter=self.get_organizations_filter(orgtype)
        )

    @property
    def parties(self):
        return self.organizations_by_type('party')

    @property
    def party_uuids(self):
        return self.organization_uuids_by_type('party')

    @property
    def party_memberships(self):
        return self.memberships_by_type('party')

    @property
    def committees(self):
        return self.organizations_by_type('committee')

    @property
    def committee_uuids(self):
        return self.organization_uuids_by_type('committee')

    @property
    def committee_memberships(self):
        return self.memberships_by_type('committee')

    @property
    def factions(self):
        return self.organizations_by_type('faction')

    @property
    def faction_uuids(self):
        return self.organization_uuids_by_type('faction')

    @property
    def faction_memberships(self):
        return self.memberships_by_type('faction')

    @property
    def motions(self):
        try:
            motions_provider = queryUtility(IMotionsProvider)

            if motions_provider:
                motions = motions_provider.motions_by_entity(IUUID(self))
                return LinkList((m.title, m.url) for m in motions)
        except:
            log.exception('could not retrieve motions')

        return []


class CompoundColumns(grok.Adapter):

    grok.name('kantonsrat-compound-columns')
    grok.provides(ICompoundColumns)
    grok.context(Interface)

    def get_compound_columns(self):
        return {
            'parties': 'party_uuids',
            'committees': 'committee_uuids',
            'factions': 'faction_uuids'
        }
