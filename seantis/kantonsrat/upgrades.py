from plone import api

from seantis.people.upgrades import (
    run_import_step_from_profile,
    upgrade_portal_type
)
from seantis.kantonsrat.types import IOrganization


def remove_faulty_type_name(context):
    run_import_step_from_profile('typeinfo', 'seantis.kantonsrat', 'default')
    api.portal.get_tool('portal_catalog').clearFindAndRebuild()


def upgrade_type_info(context):
    upgrade_portal_type(
        'seantis.kantonsrat.member', 'seantis.kantonsrat', 'default'
    )


def upgrade_membership_title(context):
    from seantis.people.upgrades import upgrade_membership_title as upgrade
    upgrade(context)


def move_to_new_membership_type(context):
    catalog = api.portal.get_tool('portal_catalog')
    memberships = [m.getObject() for m in catalog.unrestrictedSearchResults(
        portal_type='seantis.people.membership'
    )]

    for membership in memberships:
        parent = membership.aq_inner.aq_parent

        if not IOrganization.providedBy(parent):
            continue

        new_membership = api.content.create(
            type='seantis.kantonsrat.membership',
            container=parent,
            id=membership.id + '-new',
            title=membership.title,
            role=membership.role,
            note=membership.note,
            person=membership.person,
        )

        old_id = membership.id
        new_id = new_membership.id

        api.content.delete(obj=membership)
        parent.manage_renameObject(new_id, old_id)

        parent.reindexObject()
        new_membership.reindexObject()
