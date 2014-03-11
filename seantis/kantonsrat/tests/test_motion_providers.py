import json
from time import sleep

from seantis.kantonsrat import tests
from seantis.kantonsrat.motion_providers import (
    GeschaeftsverzeichnisMotionsProvider
)


class TestProvider(GeschaeftsverzeichnisMotionsProvider):

    called = 0
    json = u''

    def open_url(self):
        self.called += 1
        return self.json


class TestMotionsProvider(tests.IntegrationTestCase):

    def test_motions_caching(self):

        provider = TestProvider()
        provider.cache_lifetime = 1.0

        provider.get_motions()
        self.assertEqual(provider.called, 1)
        self.assertEqual(provider.cache_version, 0)

        provider.get_motions()
        self.assertEqual(provider.called, 1)
        self.assertEqual(provider.cache_version, 0)

        sleep(1.01)

        provider.get_motions()
        self.assertEqual(provider.called, 2)
        self.assertEqual(provider.cache_version, 1)

    def test_get_motions(self):

        provider = TestProvider()
        provider.cache_lifetime = 0

        provider.json = u'asdfasdf{{{{'
        self.assertEqual(provider.get_external_motions(), [])
        self.assertEqual(provider.get_motions(), {})

        provider.json = u''
        self.assertEqual(provider.get_external_motions(), [])
        self.assertEqual(provider.get_motions(), {})

        provider.json = json.dumps([
            dict(
                id=1,
                titel='test',
                eingereicht_von_refs=['a', 'b'],
                kommissionen_refs=['c'],
                url='https://google.ch'
            )
        ])

        self.assertEqual(provider.get_external_motions(), json.loads(
            provider.json
        ))

        for ref in ('a', 'b', 'c'):
            motions = provider.motions_by_entity(ref)

            self.assertEqual(len(motions), 1)
            self.assertEqual(motions[0].title, 'test')
            self.assertEqual(motions[0].url, 'https://google.ch')
