#!/usr/bin/env python3

import requests
from zoneinfo import ZoneInfo
from dateutil.parser import parse as parse_date
from functools import partial
from gcsa.event import Event
from itertools import chain

CSV_HEADER = "Subject, Start date, Start time, End time, Location"
TIMEZONE = ZoneInfo("America/Los_Angeles")

def merge_events(a, b):
    return Event(a.summary, start=a.start, end=b.end, location=a.location)

def events_are_abutting(a, b):
    return a.summary == b.summary and a.location == b.location and a.end == b.start

# is there a more pythonic way to name/implement this?
def events_are_same(a, b):
    return a.summary == b.summary and a.location == b.location and a.start == b.start and a.end == b.end

class Facility:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self._events = self.events()

    def csv(f, event_filter):
        return "\n".join(map(f.to_csv, filter(f.filters[event_filter], f._events)))

    def gcal(f, event_filter):
        return map(f.to_gcal, filter(f.filters[event_filter], f._events))

class SnoKing(Facility):
    location = "SnoKing"

    filters = {
        'any': lambda e: True,
        'stick_n_puck': lambda e: "Stick" in e['eventName'],
        'drop_in': lambda e: ("Drop" in e['eventName'] \
                             or "Stick" in e['eventName']) \
                             and not "Invite" in e['eventName'],
        'public': lambda e: "Public" in e['eventName']
    }

    def events(self):
        return requests.get(f'https://api.bondsports.co/v3/facilities/{self.api_id}/programs-schedule?startDate={self.start}&endDate={self.end}').json()['data']

    def _truncate_name(self, e):
        try:
            return e['eventName'][:e['eventName'].index('Stick N Puck')+12]
        except ValueError:
            return e['eventName']
    
    # def event_to_csv
    # def csv_event
    # def event_csv
    def to_csv(self, e):
        name = self._truncate_name(e)
        if not name.upper().startswith(self.rink.upper()):
            name = self.rink + ' ' + name
        location = self.location
        if len(e['spaces']) > 0:
            sheet = e['spaces'][0]['spaceName']
            location = self.location + ' '  + sheet
        return ", ".join([name, e['eventStartDate'], e['eventStartTime'], e['eventEndTime'], location])

    def to_gcal(self, e):
        name = self._truncate_name(e)
        if not name.upper().startswith(self.rink.upper()):
            name = self.rink + ' ' + name
        location = self.location
        if len(e['spaces']) > 0:
            sheet = e['spaces'][0]['spaceName']
            location = self.location + ' '  + sheet
        start = parse_date(e['eventStartDate'] + ' ' + e['eventStartTime']).replace(tzinfo=TIMEZONE)
        end = parse_date(e['eventStartDate'] + ' ' + e['eventEndTime']).replace(tzinfo=TIMEZONE)
        print(f'Creating Event({name}, {start}, {end}, {location})')
        return Event(name, start=start, end=end, location=location)


class Kirkland(SnoKing):
    api_id = 225
    rink = "Kirkland"

class Renton(SnoKing):
    api_id = 255
    rink = "Renton"

class Snoqualmie(SnoKing):
    api_id = 256
    rink = "Snoqualmie"

class WISA(Facility):
    filters = {
        'stick_n_puck': lambda e: "Stick" in e['title'],
        'drop_in': lambda e: "Stick" in e['title'] or "Drop" in e['title']
    }

    def events(self):
        # multiview=1 returns events for both rinks, but Lynnwood event
        # objects don't indicate their location.
        return requests.get(f'https://www.rectimes.app/ova/booking/getbooking?rink={self.api_id}&multiview=0&minstart=06:00:00&maxend=26:00:00&start={self.start}&end={self.end}&_=1680859722270').json()

    def to_csv(self, e):
        name = e['title']
        if not name.upper().startswith(self.rink.upper()):
            name = self.rink + ' ' + name
        date, start = e['start'].split(' ')
        _, end = e['end'].split(' ')
        return ", ".join([name, date, start, end, self.location])

    def to_gcal(self, e):
        name = e['title']
        if not name.upper().startswith(self.rink.upper()):
            name = self.rink + ' ' + name
        start = parse_date(e['start']).replace(tzinfo=TIMEZONE)
        end = parse_date(e['end']).replace(tzinfo=TIMEZONE)
        print(f'Creating Event({name}, {start}, {end}, {self.location})')
        return Event(name, start=start, end=end, location=self.location)

class OVA(WISA):
    api_id = 1145
    rink = "OVA"
    location = "Olympic View Arena"

class Lynnwood(WISA):
    api_id = 1146
    rink = "Lynnwood"
    location = "Lynnwood Ice Center"

class KCI(Facility):
    rink = "KCI"
    location = "Kraken Community Iceplex"

    filters = {
        'hockey': lambda e: e['sportId'] == 20,
        'stick_n_puck': lambda e: "Stick" in e['title'],
        'drop_in': lambda e: "Stick" in e['title'] or "Drop" in e['title']
    }

    def events(self):
        return requests.get(f'https://www.krakencommunityiceplex.com/Umbraco/api/DaySmartCalendarApi/GetEventsAsync?start={self.start}&end={self.end}&variant=2').json()

    def to_csv(self, e):
        name = self.rink + ' ' + e['title']
        date, start = e['start'].split('T')
        _, end = e['end'].split('T')
        return ", ".join([name, date, start[:-1], end[:-1], self.location])

    def to_gcal(self, e):
        name = e['title']
        if not name.upper().startswith(self.rink.upper()):
            name = self.rink + ' ' + name
        start = parse_date(e['start']).replace(tzinfo=TIMEZONE)
        end = parse_date(e['end']).replace(tzinfo=TIMEZONE)
        print(f'Creating Event({name}, {start}, {end}, {self.location})')
        return Event(name, start=start, end=end, location=self.location)

