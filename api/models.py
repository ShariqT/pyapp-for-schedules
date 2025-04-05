from django.db import models
import pyonceperday.events as scheduler
import json


# Create your models here.
class ScheduledEvent(models.Model):
  name = models.CharField(max_length=250)
  start_datetime = models.DateTimeField()
  duration = models.IntegerField()
  repeat = models.BooleanField(default=False)
  repeat_number_of_weeks = models.IntegerField(default=0)
  days = models.CharField(max_length=250)

  @classmethod
  def from_event_object(cls, event_obj):
    se = cls(name=event_obj.name, start_datetime=event_obj.start_datetime, duration=event_obj.duration)
    se.repeat = event_obj.repeat
    se.repeat_number_of_weeks = event_obj.repeat_number_of_weeks
    dayObj = { "days": [] }
    for day in event_obj.days:
      dayObj['days'].append(day.value)
    se.days = json.dumps(dayObj)
    return se

  def update_from_event(self, event):
    self.name = event.name
    self.start_datetime = event.start_datetime
    self.duration = event.duration
    self.repeat = event.repeat
    self.repeat_number_of_weeks = event.repeat_number_of_weeks
    dayObj = { "days": [] }
    for day in event.days:
      dayObj['days'].append(day.value)
    self.days = json.dumps(dayObj)

  def save_occurances(self):
    event = self.transformToEventObject()
    occurances = event.create_occurances()
    for evt in occurances:
      Occurance(name=self.name, start=evt.start, end=evt.end, event_id=self.id).save()


  def transformToEventObject(self):
    event = scheduler.Event(self.name, self.start_datetime, self.duration)
    if self.repeat is True:
      event.repeat = True
      event.repeat_number_of_weeks = self.repeat_number_of_weeks

    if self.days != "":
      daysObj = json.loads(self.days)
      dayEnumList = []
      for value in daysObj["days"]:
        dayEnumList.append(scheduler.Days(value))
      event.days = dayEnumList
    return event

class Occurance(models.Model):
  name = models.CharField(max_length=250)
  start = models.DateTimeField()
  end = models.DateTimeField()
  event_id = models.IntegerField()


  @classmethod
  def get_occurances_by_date(cls, year, month):
    return cls.objects.filter(start__year=year, start__month=month)


  def transfromToOccuranceObject(self):
    return scheduler.Occurance(self.name, self.start, self.end)
