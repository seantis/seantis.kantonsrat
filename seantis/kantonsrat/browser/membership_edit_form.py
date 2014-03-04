from five import grok

from z3c.form import field

from seantis.people.interfaces import IMembership

from seantis.kantonsrat import _
from seantis.kantonsrat.browser.base import BaseForm


class LimitedMembershipEditForm(BaseForm):
    """ Provides an edit form for memberships in seantis.kantonsrat. Said
    form does not offer all fields. It namely removes the ability to change
    the referenced person.

    """
    grok.name('edit')

    grok.context(IMembership)
    grok.require('cmf.ModifyPortalContent')

    ignoreContext = False

    label = _(u'Edit membership')
    fields = field.Fields(IMembership).select('title', 'note')

    @property
    def success_url(self):
        return self.context.aq_inner.aq_parent.absolute_url()

    @property
    def cancel_url(self):
        return self.context.aq_inner.aq_parent.absolute_url()