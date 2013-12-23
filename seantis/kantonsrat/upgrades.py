from plone import api
from seantis.people.upgrades import run_import_step_from_profile


def remove_faulty_type_name(context):
    run_import_step_from_profile(context, 'typeinfo', 'seantis.kantonsrat')
    api.portal.get_tool('portal_catalog').clearFindAndRebuild()
