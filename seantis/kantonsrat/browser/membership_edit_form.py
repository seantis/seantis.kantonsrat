from five import grok

from seantis.plonetools.browser import BaseGroup
from seantis.kantonsrat.types import IMembership
from seantis.kantonsrat import _
from seantis.kantonsrat.browser.base import BaseForm


class GeneralGroup(BaseGroup):
    label = _(u'General')

    group_fields = [
        [IMembership, ['title', 'note']]
    ]


class AdvancedGroup(BaseGroup):
    label = _(u'Advanced')

    group_fields = [
        [IMembership, ['person', 'replacement_for']]
    ]

    def update_fields(self):
        self.fields['person'].field.description = _(
            u"Don't change this value if a new members replaces this member. "
            u"Instead, change this members role and add a new member with the "
            u"new role. Otherwise the history of this organization won't be "
            u"correct anymore. "
        )


class LimitedMembershipEditForm(BaseForm):
    """ Provides an edit form for memberships in seantis.kantonsrat. Said
    form does not offer all fields. It namely removes the ability to change
    the referenced person.

    """
    grok.name('edit')

    grok.context(IMembership)
    grok.require('cmf.ModifyPortalContent')

    groups = (GeneralGroup, AdvancedGroup)

    enable_form_tabbing = True
    ignoreContext = False

    @property
    def label(self):
        return u'{organization} - {person}'.format(
            organization=self.context.aq_inner.aq_parent.Title(),
            person=self.context.person.to_object.title,
        )

    @property
    def success_url(self):
        return self.context.aq_inner.aq_parent.absolute_url()

    @property
    def cancel_url(self):
        return self.context.aq_inner.aq_parent.absolute_url()
