from datetime import date
from freezegun import freeze_time
from plone import api
from seantis.kantonsrat import tests


class TestOrganization(tests.IntegrationTestCase):

    def test_membership_by_state(self):
        self.login('admin')

        container = self.new_temporary_folder()

        organization = api.content.create(
            container=container,
            type='seantis.kantonsrat.organization',
            title=u'White House'
        )

        presidents = api.content.create(
            container=container,
            type='seantis.people.list',
            title=u'Presidents'
        )

        bush = api.content.create(
            container=presidents,
            type='seantis.kantonsrat.member',
            title=u'George W. Bush',
            firstname='George W.',
            lastname='Bush',
        )

        first_term = api.content.create(
            container=organization,
            type='seantis.kantonsrat.membership',
            title=u'43rds First Term',
            role=u'President',
            person=bush
        )

        self.assertEqual(len(organization.memberships(state='all')), 1)
        self.assertEqual(len(organization.memberships(state='active')), 1)
        self.assertEqual(len(organization.memberships(state='inactive')), 0)
        self.assertEqual(len(organization.memberships(state='future')), 0)

        second_term = api.content.create(
            container=organization,
            type='seantis.kantonsrat.membership',
            title=u'43rds Second Term',
            role=u'President',
            person=bush,
            replacement_for=first_term
        )

        self.assertEqual(len(organization.memberships(state='all')), 2)
        self.assertEqual(len(organization.memberships(state='active')), 1)
        self.assertEqual(len(organization.memberships(state='inactive')), 1)
        self.assertEqual(len(organization.memberships(state='future')), 0)

        obama = api.content.create(
            container=presidents,
            type='seantis.kantonsrat.member',
            title=u'Barack H. Obama',
            firstname='Barack H.',
            lastname='Obama',
        )

        first_term = api.content.create(
            container=organization,
            type='seantis.kantonsrat.membership',
            title=u'44ths First Term',
            role=u'President',
            person=obama,
            replacement_for=second_term
        )

        self.assertEqual(len(organization.memberships(state='all')), 3)
        self.assertEqual(len(organization.memberships(state='active')), 1)
        self.assertEqual(len(organization.memberships(state='inactive')), 2)
        self.assertEqual(len(organization.memberships(state='future')), 0)

    def test_membership_by_state_with_dates(self):
        # the test_membership_by_state test relies on 'replacement_for'
        # to determine the active/inactive states, this can also accomplished
        # solely by using start/end dates

        self.login('admin')

        container = self.new_temporary_folder()

        organization = api.content.create(
            container=container,
            type='seantis.kantonsrat.organization',
            title=u'White House'
        )

        presidents = api.content.create(
            container=container,
            type='seantis.people.list',
            title=u'Presidents'
        )

        bush = api.content.create(
            container=presidents,
            type='seantis.kantonsrat.member',
            title=u'George W. Bush',
            firstname='George W.',
            lastname='Bush',
        )

        api.content.create(
            container=organization,
            type='seantis.kantonsrat.membership',
            title=u'43rds First Term',
            role=u'President',
            person=bush,
            start=date(2001, 1, 20),
            end=date(2005, 1, 19)
        )

        api.content.create(
            container=organization,
            type='seantis.kantonsrat.membership',
            title=u'43rds Second Term',
            role=u'President',
            person=bush,
            start=date(2005, 1, 20),
            end=date(2009, 1, 19)
        )

        memberships = lambda state: organization.memberships(state=state)

        with freeze_time(date(2001, 1, 19)):
            self.assertEqual(len(memberships(state='all')), 2)
            self.assertEqual(len(memberships(state='active')), 0)
            self.assertEqual(len(memberships(state='inactive')), 0)
            self.assertEqual(len(memberships(state='future')), 2)

        with freeze_time(date(2001, 1, 20)):
            self.assertEqual(len(memberships(state='all')), 2)
            self.assertEqual(len(memberships(state='active')), 1)
            self.assertEqual(len(memberships(state='inactive')), 0)
            self.assertEqual(len(memberships(state='future')), 1)

        with freeze_time(date(2005, 1, 19)):
            self.assertEqual(len(memberships(state='all')), 2)
            self.assertEqual(len(memberships(state='active')), 1)
            self.assertEqual(len(memberships(state='inactive')), 0)
            self.assertEqual(len(memberships(state='future')), 1)

        with freeze_time(date(2005, 1, 20)):
            self.assertEqual(len(memberships(state='all')), 2)
            self.assertEqual(len(memberships(state='active')), 1)
            self.assertEqual(len(memberships(state='inactive')), 1)
            self.assertEqual(len(memberships(state='future')), 0)

        with freeze_time(date(2009, 1, 19)):
            self.assertEqual(len(memberships(state='all')), 2)
            self.assertEqual(len(memberships(state='active')), 1)
            self.assertEqual(len(memberships(state='inactive')), 1)
            self.assertEqual(len(memberships(state='future')), 0)

        with freeze_time(date(2009, 1, 20)):
            self.assertEqual(len(memberships(state='all')), 2)
            self.assertEqual(len(memberships(state='active')), 0)
            self.assertEqual(len(memberships(state='inactive')), 2)
            self.assertEqual(len(memberships(state='future')), 0)
