from django.shortcuts import render
import json
from . import utils
from pyonceperday.events import Days
from pyonceperday.exceptions import OverMaxDurantion, OverRepeatLimit
from . import models
# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse

def index(request):
  return HttpResponse("Event API v1")


def create_new_event(request):
  if request.method != "POST":
    res = HttpResponse("Nope!")
    res.status_code = 401
    return res

  event_data = json.loads(request.body)
  
  try:
    event = utils.create_new_event(event_data)
  except(Exception) as e:
    res = HttpResponse(f"there was an error processing this event.: {e}")
    res.status_code=500
    return res
  
  try:  
    utils.check_for_overlapping_events(event)
  except(Exception):
    res = HttpResponse(f"this event conflicts with existing events")
    res.status_code = 500
    return res

  se = models.ScheduledEvent.from_event_object(event)
  se.save()
  se.save_occurances()
  return JsonResponse({"event": {"name": se.name, "id": se.id }})


def update_event(request, event_id):
  if request.method != "POST":
    res = HttpResponse("Nope!")
    res.status_code = 401
    return res
  
  try:
    se, occurances = utils.get_event_by_id(event_id)
  except(models.ScheduledEvent.DoesNotExist):
    res = HttpResponse("Cannot find a record with that id")
    res.status_code = 500
    return res
  
  occurances.delete()
  event_data = json.loads(request.body)
  

  try:
    event = utils.create_new_event(event_data)
  except(Exception) as e:
    res = HttpResponse(f"there was an error processing this event. missing: {e}")
    res.status_code=500
    return res
  
  try:  
    utils.check_for_overlapping_events(event)
  except(Exception):
    res = HttpResponse(f"this event conflicts with existing events")
    res.status_code = 500
    return res

  se.update_from_event(event)
  se.save()
  se.save_occurances()
  
  return JsonResponse({"event": {"name": se.name, "id": se.id }})

def get_event(request, event_id):
  if request.method != "GET":
    res = HttpResponse("Nope!")
    res.status_code = 405
    return res
  try:
    se, occurances = utils.get_event_by_id(event_id)
  except(models.ScheduledEvent.DoesNotExist):
    res = HttpResponse("Could not find a record for this id")
    res.status_code = 500
    return res

  
  data = {"event": {
    "name": se.name,
    "start": se.start_datetime.isoformat(),
    "occurances":[],
    "days": []
  }}

  se_days = json.loads(se.days)
  for day in se_days["days"]:
    d = Days(day)
    data['event']['days'].append(d.name)

  for evt in occurances:
    data["event"]["occurances"].append({ "start": evt.start.isoformat(), "end": evt.end.isoformat() })
  
  return JsonResponse(data)
