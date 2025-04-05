from django.test import TestCase, Client
from api.models import ScheduledEvent, Occurance
from api import utils
import pytz, json
from datetime import datetime, timedelta

class OverlapTest(TestCase):
    def setUp(self):
        year = 2025
        month = 4
        day = 11
        Occurance.objects.create(name="t1", 
          start=datetime(year=year,month=month, day=11, hour=9, minute=0, tzinfo=pytz.UTC),
          end=datetime(year=year,month=month, day=11, hour=9, minute=20, tzinfo=pytz.UTC),
          event_id=1)
        Occurance.objects.create(name="t2", 
          start=datetime(year=year,month=month, day=11, hour=10, minute=15, tzinfo=pytz.UTC),
          end=datetime(year=year,month=month, day=11, hour=10, minute=30, tzinfo=pytz.UTC),
          event_id=1)
        Occurance.objects.create(name="t3", 
          start=datetime(year=year,month=month, day=11, hour=11, minute=0, tzinfo=pytz.UTC),
          end=datetime(year=year,month=month, day=11, hour=12, minute=30, tzinfo=pytz.UTC),
          event_id=1)

    def test_check_if_overlap(self):
        event = utils.create_new_event({"name": "test", "duration": 15, "start": "2025-04-11T10:00", "days":[5]})
        res = utils.check_for_overlapping_events(event)
        self.assertEqual(res, None)

        event = utils.create_new_event({"name": "test", "duration": 15, "start": "2025-05-11T14:00", 'days':[5]})
        res = utils.check_for_overlapping_events(event)
        self.assertEqual(res, None)

        with self.assertRaises(Exception) as ex:
          event = utils.create_new_event({"name": "test", "duration": 60, "start": "2025-04-11T11:00", "days":[5]})
          utils.check_for_overlapping_events(event)
          self.assertIn(ex, "t3")

      

class EventCreateTestCase(TestCase):

    def test_create_new_event_raises_exception(self):
        data = {'name': "test", "duration": 20}
        with self.assertRaises(Exception):
          utils.create_new_event(data)
    
    def test_transformation_to_scheduled_object_works(self):
        start = datetime(year=2025, month=4, day=4, hour=13, minute=0, tzinfo=pytz.UTC)
        event = ScheduledEvent(name="test", start_datetime=start, duration=30)
        result = event.transformToEventObject()
        self.assertEqual(len(result.days), 1)
        self.assertEqual(result.name, "test")
        self.assertEqual(result.duration, 30)

        event = ScheduledEvent(name="test", start_datetime=start, duration=30)
        event.repeat = True
        event.repeat_number_of_weeks = 3
        event.days = json.dumps({"days": [2,5,6]})
        result = event.transformToEventObject()
        self.assertEqual(len(result.days), 3)
        self.assertEqual(result.name, "test")
        self.assertEqual(result.duration, 30)

    def test_create_API_route(self):
        c = Client()
        event_data = json.dumps({"name": "test", "duration": 30})
        res = c.post("/api/v1/create/", event_data, content_type='application/json')
        self.assertEqual(res.status_code, 500)

        event_data = json.dumps({"name": "test", "duration": 30, "start": "2025-05-09T14:00", "days":[5] })
        res = c.post("/api/v1/create/", event_data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        oc = Occurance.objects.filter(event_id=data["event"]["id"])
        self.assertEqual(len(oc), 1)
        self.assertEqual(data['event']['name'], "test")

class GetEventTestCase(TestCase):
    def setUp(self):
        start = datetime(year=2025, month=4, day=8, hour=11, minute=0, tzinfo=pytz.UTC)
        ScheduledEvent.objects.create(
          name="test", 
          start_datetime=start, 
          duration=30,
          days=json.dumps({"days":[4,5]}))

        Occurance.objects.create(
          name="test",
          start= start.replace(day=10),
          end = start + timedelta(minutes=30),
          event_id=1
        )

        Occurance.objects.create(
          name="test",
          start=start.replace(day=11),
          end = start + timedelta(minutes=30),
          event_id=1
        )

    def test_get_event_view(self):
        c = Client()
        res = c.get("/api/v1/get/1/")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEqual(data['event']['name'], "test")
        self.assertEqual(data['event']['days'][0], "THURSDAY")
        self.assertEqual(data['event']['days'][1], "FRIDAY")
        self.assertEqual(len(data['event']['occurances']), 2)


