from z3c.relationfield.schema import RelationChoice

from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.dexterity.content import Container

from seantis.people.interfaces import IMembership as IPeopleMembership
from seantis.kantonsrat import _


class Membership(Container):
    pass


class IMembership(IPeopleMembership):

    replacement_for = RelationChoice(
        title=_(u"Replacement for"),
        description=_(u"The membership which this membership replaces"),
        source=ObjPathSourceBinder(
            object_provides=(
                'seantis.kantonsrat.types.membership.IKantonsratMembership'
            )
        ),
        required=False
    )
