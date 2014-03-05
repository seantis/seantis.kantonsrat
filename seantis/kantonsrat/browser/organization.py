from collections import namedtuple

from plone import api
from five import grok

from zope.security import checkPermission

from seantis.kantonsrat.types import IOrganization
from seantis.kantonsrat.browser.base import BaseView


class OrganizationView(BaseView):

    permission = 'zope2.View'
    grok.require(permission)
    grok.context(IOrganization)
    grok.name('view')

    template = grok.PageTemplateFile('templates/organization.pt')

    def members(self):
        Member = namedtuple(
            'Member', ['role', 'person', 'url', 'note', 'membership_edit']
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
            person_brain = catalog(
                path={'query': membership.person.to_path}
            )[0]

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
                    membership_edit
                )
            )

        return members
