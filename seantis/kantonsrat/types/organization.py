from time import mktime
from datetime import date

from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.indexer import indexer
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.dexterity.content import Container
from plone.directives import form

from collective.dexteritytextindexer import searchable

from seantis.kantonsrat import _


organization_types = SimpleVocabulary(
    [
        SimpleTerm(value='committee', title=_(u'Committee')),
        SimpleTerm(value='faction', title=_(u'Faction')),
        SimpleTerm(value='party', title=_(u'Party'))
    ]
)


class IOrganization(form.Schema):

    searchable('type')
    type = schema.Choice(
        title=_(u'Type'),
        source=organization_types,
        default='committee'
    )

    searchable('title')
    title = schema.TextLine(
        title=_(u'Title')
    )

    searchable('description')
    description = schema.Text(
        title=_(u'Description')
    )

    searchable('portrait')
    form.widget(portrait=WysiwygFieldWidget)
    portrait = schema.Text(
        title=_(u'Portrait'),
        required=False
    )

    active = schema.Bool(
        title=_(u'Active'),
        description=_(
            u"Inactive organisations are not listed in the member's view and "
            u"are not available in the list of organizations.<br/> They are, "
            u"however, still available through their url.<br/> "
            u"Active organisations are also shown depending on their "
            u"start/end date, if those are provided.<br/>"
            u"Inactive organisations are never shown, independent of any dates"
        ),
        required=True,
        default=True
    )

    form.widget('start', years_range=(-10, 25))
    start = schema.Date(
        title=_(u'Start'),
        description=_(
            u"Date from which the organization is visible (if active)."
        ),
        required=False
    )

    form.widget('end', years_range=(-10, 25))
    end = schema.Date(
        title=_(u'Start'),
        description=_(
            u"Date after which the organization is invisible."
        ),
        required=False
    )

    @invariant
    def has_valid_daterange(Organization):
        if Organization.start is None:
            return

        if Organization.end is None:
            return

        if Organization.start > Organization.end:
            raise Invalid(_(u"The start date is set after the end date."))


@indexer(IOrganization)
def organization_type(obj):
    return obj.type


@indexer(IOrganization)
def organization_active(obj):
    return obj.active


@indexer(IOrganization)
def organization_start(obj):
    # I don't feel like mucking around with Zope's Datetime and since this
    # product is as Swiss as it probably gets I don't see the use of
    # introducing timezones at this point. So I use numerics.

    return mktime((obj.start or date.min).timetuple())


@indexer(IOrganization)
def organization_end(obj):
    # see above

    return mktime((obj.end or date.min).timetuple())


class Organization(Container):

    def exclude_from_nav(self):
        if not self.active:
            return True

        today = date.today()
        start, end = (self.start or date.min), (self.start or date.min)

        return not (start <= today and today <= end)
