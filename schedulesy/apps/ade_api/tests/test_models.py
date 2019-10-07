import collections
import os
import shutil
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase

from ..models import AdeConfig, LocalCustomization, Resource


User = get_user_model()


class AdeConfigModelTestCase(TestCase):

    def test_save_singleton(self):
        AdeConfig.objects.create(
            ade_url='https://adewebcons-test.unistra.fr/',
            parameters={'projectId': '1'}
        )

        with self.assertRaises(IntegrityError):
            AdeConfig.objects.create(
                ade_url='https://adewebcons-test.unistra.fr/',
                parameters={'projectId': '2'}
            )


class LocalCustomizationGenerateEventsTestCase(TestCase):

    fixtures = ['tests/resources']

    def setUp(self):
        self.user_owner = User.objects.create_user('owner', password='pass')

    def test_with_empty_resources(self):
        lc = LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner')
        data = lc.generate_events()

        self.assertDictEqual(data, {})

    def test_with_single_resource(self):
        res_bcd_media = Resource.objects.get(ext_id='1616')
        lc = LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner')
        lc.resources.add(res_bcd_media)
        data = lc.generate_events()

        self.assertEqual(len(data['events']), 1)

    def test_with_multiple_resources(self):
        res_bcd_media = Resource.objects.get(ext_id='1616')
        instructor = Resource.objects.get(ext_id='23390')
        lc = LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner')
        lc.resources.add(res_bcd_media, instructor)
        data = lc.generate_events()

        self.assertEqual(len(data['events']), 2)
        self.assertEqual(len(data['classrooms']), 2)
        self.assertEqual(len(data['instructors']), 2)
        self.assertEqual(len(data['trainees']), 2)


class LocalCustomizationGenerateIcsCalendarTestCase(TestCase):

    fixtures = ['tests/resources']

    def setUp(self):
        self.user_owner = User.objects.create_user('owner', password='pass')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def _assertIcsFields(self, filename, fields):
        with open(filename, 'r') as fh:
            d = collections.defaultdict(list)
            for k, v in map(lambda x: x.strip().split(':', 1), fh.readlines()):
                d[k].append(v)

            for k, v in fields.items():
                self.assertListEqual(
                    sorted(e.replace('\\', '') for e in d[k]),
                    sorted(v if isinstance(v, list) else [v]))

    def test_ics_calendar_filename(self):
        lc = LocalCustomization(username='owner')
        self.assertEqual(lc.ics_calendar_filename, 'owner.ics')

    def test_with_empty_resources(self):
        lc = LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner')
        lc.generate_ics_calendar()

        self.assertFalse(os.path.isfile(
            os.path.join(settings.MEDIA_ROOT, lc.ics_calendar_filename)))

    def test_with_single_resource(self):
        res_bcd_media = Resource.objects.get(ext_id='1616')
        lc = LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner')
        lc.resources.add(res_bcd_media)
        lc.generate_ics_calendar()

        # Testing formatted fields
        self._assertIcsFields(
            os.path.join(settings.MEDIA_ROOT, lc.ics_calendar_filename),
            {
                'LOCATION': 'BCD Media (COL  -SITE COLMAR, ESPE COLMAR BATIMENT PRINCIPAL)'
            }
        )

    def test_with_multiple_resources(self):
        res_bcd_media = Resource.objects.get(ext_id='1616')
        instructor = Resource.objects.get(ext_id='23390')
        lc = LocalCustomization.objects.create(
            customization_id='1', directory_id='42', username='owner')
        lc.resources.add(res_bcd_media, instructor)
        lc.generate_ics_calendar()

        # Testing formatted fields
        self._assertIcsFields(
            os.path.join(settings.MEDIA_ROOT, lc.ics_calendar_filename),
            {
                'LOCATION': [
                    'BCD Media (COL  -SITE COLMAR, ESPE COLMAR BATIMENT PRINCIPAL)',
                    'A1.13 Informatique So (A1.16) (SCH  -SITE SCHILTIGHEIM, IUT LOUIS PASTEUR, TP)'
                ]
            }
        )
