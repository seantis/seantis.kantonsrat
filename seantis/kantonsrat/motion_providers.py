import logging
log = logging.getLogger('seantis.kantonsrat')

import json
import urllib2

from datetime import datetime
from itertools import chain

from zope.interface import implements
from plone.memoize import ram

from seantis.kantonsrat.interfaces import IMotion, IMotionsProvider


class Motion(object):

    implements(IMotion)

    def __init__(self, title, url):
        self.title = title
        self.url = url


class GeschaeftsverzeichnisMotionsProvider(object):

    implements(IMotionsProvider)

    # xxx make configurable through controlpanel
    url = u'https://geschaefte.4teamwork.ch/api/geschaefte.json'
    timeout = 5.0  # seconds
    cache_lifetime = 3600.0  # seconds

    def __init__(self):
        self._cache_version = 0
        self._last_fetch = None

    def motions_by_entity(self, entity_uuid):
        motions = list(
            Motion(title=m['titel'], url=m['url'])
            for m in self.get_motions().get(entity_uuid, [])
        )

        return sorted(motions, key=lambda motion: motion.title)

    @ram.cache(lambda method, self: self.cache_version)
    def get_motions(self):
        return self.force_get_motions()

    def force_get_motions(self):

        external_motions_by_uuid = {}

        for external_motion in self.get_external_motions():
            uuids = chain(
                external_motion.get('eingereicht_von_refs', []),
                external_motion.get('kommissionen_refs', [])
            )
            normalize = lambda uid: uid.lower().replace('-', '')

            for uuid in (normalize(uid) for uid in uuids):
                if uuid in external_motions_by_uuid:
                    external_motions_by_uuid[uuid].append(external_motion)
                else:
                    external_motions_by_uuid[uuid] = [external_motion]

        return external_motions_by_uuid

    @property
    def cache_version(self):
        last_fetch = (self._last_fetch or datetime.utcnow())
        cache_age = (datetime.utcnow() - last_fetch).total_seconds()

        if cache_age > self.cache_lifetime:
            self._cache_version += 1

        return self._cache_version

    def open_url(self):
        try:
            log.info('fetching motions from {}'.format(self.url))
            data = urllib2.urlopen(self.url, timeout=self.timeout).read()
        except:
            log.exception('could not fetch motions from {}'.format(self.url))
            data = ''

        return data.strip()

    def get_external_motions(self):
        # Set the timestamp before the fetch, if it fails we won't retry
        # until the timeout is up. This has the potential for missing data,
        # but it will make sure the website reacts fast at all times.
        self._last_fetch = datetime.utcnow()

        raw_data = self.open_url()
        if raw_data:
            try:
                return json.loads(raw_data)
            except:
                log.exception('Could not parse json')
                return []
        else:
            return []
