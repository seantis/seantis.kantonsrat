from collections import namedtuple
from datetime import datetime, date
from plone import api
from seantis.kantonsrat import _

from pdfdocument.document import MarkupParagraph
from reportlab.lib.units import cm
from seantis.kantonsrat.reports.base import Report


class MembershipInfo(object):

    __slots__ = ('name', 'role', 'address_parts', 'party', 'elected')

    def __init__(self, name, role, address_parts, party):
        self.name = name
        self.role = role
        self.address_parts = address_parts
        self.party = party

    def get_text(self):
        parts = list()
        if self.name:
            parts.append(self.name)
        if self.role:
            parts.append(self.role)
        if self.address_parts:
            parts.extend(self.address_parts)

        return ', '.join(parts)


MembershipNotes = namedtuple(
    'MembershipNotes', ['notes', 'reference']
)


class OrganizationsReport(Report):

    def populate(self):

        report_date = date.today()

        self.pdf.h1(self.context.title)
        self.pdf.h2(self.translate(_(u'Content')))
        self.pdf.table_of_contents()
        self.pdf.pagebreak()

        table_columns = [1.5*cm, 10*cm, 2*cm]

        for organization in self.get_organizations(report_date):

            self.reset_references()

            self.pdf.h1(organization.title)
            self.pdf.p(organization.description)
            self.pdf.spacer()

            tables = self.get_membership_tables(organization, report_date)

            for table_data in tables:
                if table_data:
                    self.pdf.table(
                        self.wrap_rows_in_paragraphs(table_data),
                        table_columns
                    )
                    self.pdf.spacer()

            if organization.start:
                self.pdf.p(self.translate(_(u'Election on ${date}', mapping={
                    'date': api.portal.get_localized_time(
                        datetime=datetime.combine(
                            organization.start, datetime.min.time()
                        )
                    )
                })))

            self.pdf.spacer()
            self.pdf.spacer()

    def get_reference(self):
        self.reference_count += 1
        return self.reference_count * '*'

    def reset_references(self):
        self.reference_count = 0

    def get_person_party(self, person):
        parties = person.parties
        return parties and parties[0] or ''

    def get_membership_info(self, membership):
        person = membership.person.to_object
        name = ' '.join((person.lastname, person.firstname))
        address_parts = [
            p.strip() for p in person.address.split('\n') if p.strip()
        ]
        party = self.get_person_party(person)

        return MembershipInfo(name, membership.role, address_parts, party)

    def wrap_rows_in_paragraphs(self, table):
        for row in table:
            for ix, column in enumerate((row or [])):
                row[ix] = MarkupParagraph(column, self.pdf.style.normal)

        return table

    def get_membership_notes(self, membership):
        if not membership.replacement_for and not membership.note:
            return None

        replaced_membership = membership.replacement_for.to_object

        notes = []

        if membership.replacement_for:
            info = self.get_membership_info(replaced_membership)
            info.elected = membership.start
            notes.append(info)

        if membership.note:
            notes.append(membership.note)

        return MembershipNotes(notes, self.get_reference())

    def get_membership_tables(self, organization, report_date):
        brains = organization.memberships('present', report_date)
        memberships = (o.getObject() for o in brains)

        memberships_table = []
        notes_table = []

        for membership in memberships:
            info = self.get_membership_info(membership)
            notes = self.get_membership_notes(membership)

            memberships_table.append([
                notes and notes.reference, info.get_text(), info.party
            ])

            for ix, note in enumerate(notes and notes.notes or []):
                if isinstance(note, MembershipInfo):
                    if note.elected:
                        text = _(
                            u'Replacement for ${name}, elected on ${date}',
                            mapping={
                                'name': note.get_text(),
                                'date': api.portal.get_localized_time(
                                    datetime=datetime.combine(
                                        note.elected, datetime.min.time()
                                    )
                                )
                            }
                        )

                    else:
                        text = _(u'Replacement for ${name}', mapping={
                            'name': note.get_text()
                        })

                    text = self.translate(text)
                    party = note.party
                else:
                    text = note
                    party = ''

                notes_table.append([
                    ix == 0 and notes.reference or '', text, party
                ])

        return memberships_table, notes_table

    def get_organizations(self, report_date):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(
            path={'query': '/'.join(self.context.getPhysicalPath())},
            portal_type='seantis.kantonsrat.organization',
            sort_on='sortable_title'
        )

        organizations = []

        for brain in brains:
            if report_date < (brain.start or date.min):
                continue

            if report_date > (brain.end or date.max):
                continue

            organizations.append(brain.getObject())

        return sorted(organizations, key=lambda o: o.title)
