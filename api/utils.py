from pyonceperday.events import Event, is_occurance_overlapping, Days
from datetime import datetime
import pytz
from . import models

def create_new_event(event_data):
  # check for required keys
  required_keys = ["name", "start", "duration", "days"]
  for name in required_keys:
    if name not in event_data.keys():
      raise Exception("Missing required event information")
  
  start = datetime.fromisoformat(event_data['start'])
  start = start.replace(tzinfo=pytz.UTC)
  event = Event(event_data['name'], start, event_data['duration'])
  event.days = []
  if 'repeat' in event_data.keys():
    if event_data['repeat'] == 1:
      event.repeat = True
    else:
      event.repeat = False
    event.repeat_number_of_weeks = event_data['number_of_weeks']
  
  for day in event_data["days"]:
    event.days.append(Days(day))
  return event


def get_event_by_id(event_id):
  se = models.ScheduledEvent.objects.get(id=event_id)
  occurances = models.Occurance.objects.filter(event_id=event_id)
  return (se, occurances)

def check_for_overlapping_events(event):
  occurances = models.Occurance.get_occurances_by_date(event.start_datetime.year, event.start_datetime.month)
  if len(occurances) == 0:
    return None
  event_occurances = event.create_occurances()
  for eo in event_occurances:
    for to in occurances:
      to_obj = to.transfromToOccuranceObject()
      if is_occurance_overlapping(eo, to_obj) is True:
        raise Exception(f"overlapping event with {to.name} at {to.start} to {to.end}")
  return None

