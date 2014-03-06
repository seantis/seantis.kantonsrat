from collections import namedtuple

from five import grok
from zope.interface import Interface
from zope.security import checkPermission

from plone import api

from seantis.kantonsrat import _
from seantis.kantonsrat.browser.base import BaseView


class View(BaseView):
    """A numer of macros for use with seantis.people"""

    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('seantis-kantonsrat-macros')

    template = grok.PageTemplateFile('templates/macros.pt')

    def __getitem__(self, key):
        return self.template._template.macros[key]

    def get_brain_from_relation(self, relation):
        if not relation:
            return None

        catalog = api.portal.get_tool('portal_catalog')
        results = catalog(path={'query': relation.to_path})

        return results and results[0] or None

    def as_simplified_structure(self, memberships):
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

            yield Member(
                membership.role,
                person_brain.Title,
                person_brain.getURL(),
                membership.note,
                replacement_for,
                membership_edit
            )
