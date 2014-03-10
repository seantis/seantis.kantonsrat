from five import grok

from zope.schema.interfaces import IContextSourceBinder
from z3c.relationfield.schema import RelationChoice

from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.uuid.interfaces import IUUID

from seantis.people.interfaces import IMembership as IPeopleMembership
from seantis.people.content import Membership as PeopleMembership
from seantis.kantonsrat.types import IOrganization
from seantis.kantonsrat import _


class Membership(PeopleMembership):

    @property
    def replacement_for_uuid(self):
        if self.replacement_for:
            return IUUID(self.replacement_for.to_object)
        else:
            return None


@grok.provider(IContextSourceBinder)
def available_memberships(context):

    if IOrganization.providedBy(context):
        path = {
            'query': '/'.join(context.getPhysicalPath()),
            'depth': '1'
        }
    else:
        path = {
            'query': '/'.join(context.aq_inner.aq_parent.getPhysicalPath()),
            'depth': '1'
        }

    query = {
        'portal_type': 'seantis.kantonsrat.membership',
        'path': path
    }

    return ObjPathSourceBinder(navigation_tree_query=query).__call__(context)


class IMembership(IPeopleMembership):

    replacement_for = RelationChoice(
        title=_(u"Replacement for"),
        description=_(u"The membership which this membership replaces"),
        source=available_memberships,
        required=False
    )