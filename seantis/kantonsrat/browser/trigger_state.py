from five import grok
from zope.interface import Interface
from plone import api

from seantis.kantonsrat.browser.base import BaseView


class TriggerState(BaseView):

    grok.context(Interface)
    grok.require('cmf.ModifyPortalContent')

    grok.name('trigger-state')

    def render(self):
        catalog = api.portal.get_tool('portal_catalog')
        organizations = catalog.searchResults({
            'portal_type': 'seantis.kantonsrat.organization'
        })

        for organization in organizations:
            organization.getObject().reindexObject()
