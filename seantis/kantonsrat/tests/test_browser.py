from seantis.kantonsrat import tests


class TestBrowser(tests.FunctionalTestCase):

    def setUp(self):
        super(TestBrowser, self).setUp()
        self.baseurl = self.portal.absolute_url()
        self.admin_browser = browser = self.new_admin_browser()

        browser.open(self.baseurl + '/createObject?type_name=Folder')
        browser.getControl('Title').value = 'testfolder'
        browser.getControl('Save').click()

        self.folder_url = self.baseurl + '/testfolder'
        self.infolder = lambda url: self.folder_url + url

    def tearDown(self):
        self.admin_browser.open(self.infolder('/delete_confirmation'))
        self.admin_browser.getControl('Delete').click()

        super(TestBrowser, self).tearDown()

    def new_admin_browser(self):
        browser = self.new_browser()
        browser.login_admin()

        return browser

    def new_member_list(self, title):
        browser = self.new_admin_browser()

        browser.open(self.infolder('/++add++seantis.people.list'))
        browser.getControl(name='form.widgets.title').value = title
        browser.getControl('Save').click()

        return self.infolder('/{}'.format(title.lower()))

    def new_member(self, first_name, last_name, memberlist='members'):
        browser = self.new_admin_browser()

        browser.open(self.infolder('/{}'.format(memberlist)))
        self.assertIn('No people in the list.', browser.contents)

        browser.open(
            self.infolder(
                '/{}/++add++seantis.kantonsrat.member'.format(memberlist)
            )
        )
        browser.getControl('First Name').value = first_name
        browser.getControl('Last Name').value = last_name
        browser.getControl('Save').click()

        return self.infolder('/{}/{}-{}'.format(
            memberlist, last_name.lower(), first_name.lower()
        ))

    def test_add_member(self):
        browser = self.new_admin_browser()
        memberlist_url = self.new_member_list('members')

        browser.open(self.new_member('Frank', 'Underwood'))
        self.assertIn('Underwood Frank', browser.contents)

        browser.open(memberlist_url)
        self.assertIn('Frank', browser.contents)
        self.assertIn('Underwood', browser.contents)
