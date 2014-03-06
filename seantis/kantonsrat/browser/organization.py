from collections import namedtuple

from plone import api
from five import grok

from zope.security import checkPermission

from seantis.kantonsrat import _
from seantis.kantonsrat.types import IOrganization
from seantis.kantonsrat.browser.base import BaseView


class OrganizationView(BaseView):

    permission = 'zope2.View'
    grok.require(permission)
    grok.context(IOrganization)
    grok.name('view')

    template = grok.PageTemplateFile('templates/organization.pt')

    def get_brain_from_relation(self, relation):
        if not relation:
            return None

        catalog = api.portal.get_tool('portal_catalog')
        results = catalog(path={'query': relation.to_path})

        return results and results[0] or None

    def members(self):
        Member = namedtuple(
            'Member', [
                'role',
                'person',
                'url',
                'note',
                'replacement_for',
                'membership_edit'
            ]
        )

        folder_path = '/'.join(self.context.getPhysicalPath())

        catalog = api.portal.get_tool('portal_catalog')
        memberships = catalog(
            path={'query': folder_path, 'depth': 1},
            portal_type='seantis.kantonsrat.membership',
            sort_on='getObjPositionInParent',
        )

        members = []
        for brain in memberships:
            membership = brain.getObject()
            person_brain = self.get_brain_from_relation(membership.person)

            replacement_for_brain = self.get_brain_from_relation(
                membership.replacement_for
            )

            replacement_for = replacement_for_brain and _(
                u'Replacement for ${name}', mapping={
                    'name': replacement_for_brain.Title.decode('utf-8')
                }
            ) or u''

            if checkPermission('cmf.ModifyPortalContent', membership):
                membership_edit = membership.absolute_url() + '/edit'
            else:
                membership_edit = None

            members.append(
                Member(
                    membership.role,
                    person_brain.Title,
                    person_brain.getURL(),
                    membership.note,
                    replacement_for,
                    membership_edit
                )
            )

        return members
