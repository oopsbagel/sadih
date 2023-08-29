import json
import requests
from zoneinfo import ZoneInfo
from dateutil.parser import parse as dateutil_parse
from functools import partial
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from itertools import chain

CSV_HEADER = "Subject, Start date, Start time, End time, Location"
PACIFIC = ZoneInfo("America/Los_Angeles")
UTC = ZoneInfo("UTC")

def date_filter(start, end, event):
    # Some rink APIs do not strictly respect request start/end dates.
    return event.start >= start and event.end <= end

def merge_events(a, b):
    return Event(a.summary, start=a.start, end=b.end, location=a.location)

def events_are_abutting(a, b):
    return a.summary == b.summary and a.location == b.location and a.end == b.start

# is there a more pythonic way to name/implement this?
def events_are_same(a, b):
    return a.summary == b.summary and a.location == b.location and a.start == b.start and a.end == b.end

def subtract_events(left_events, right_events):
    """ Return left_events not found in right_events """
    return [e for e in left_events
            if not any(map(partial(events_are_same, e), right_events))]

def combine_like_events(events):
    r = list(events)
    i = 0
    while i+1 < len(r):
        if events_are_abutting(r[i], r[i+1]) or events_are_same(r[i], r[i+1]):
            print(f"{r[i]} and {r[i+1]} found to be the same")
            r = r[:i] + [merge_events(r[i], r[i+1])] + r[i+2:]
        else:
            i = i + 1
    return r

class Rink:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.api_events = self._events()

    def _parse_date(self, date):
        return dateutil_parse(date).replace(tzinfo=PACIFIC)

    def gcal(f, event_filter):
        return filter(partial(date_filter, f.start, f.end), map(f.to_gcal, filter(f.filters[event_filter], f.api_events)))


class Google(Rink):
    def _events(self):
        calendar = GoogleCalendar(self.snp_id)
        events = list(calendar.get_events(self.start, self.end))
        for recurring_event in filter(lambda e: e.recurrence, calendar):
            events += list(filter(partial(date_filter, self.start, self.end), calendar.get_instances(recurring_event)))
        return filter(lambda e: e.summary is not None, events)

    def to_gcal(self, e):
        name = self.rink + " " + e.summary
        print(f'Creating Event({name}, {e.start}, {e.end}, {self.location})')
        return Event(name, start=e.start, end=e.end, location=self.location, description=e.description)


class Everett(Google):
    rink = "Everett"
    location = "Angel of the Winds Community Rink"
    snp_id = "sk8sm8vjh0nqap97cuhshajscc@group.calendar.google.com"

    # Events are organised into subcalendars by the rink, so filters
    # as I have otherwise implemented them are useless.
    filters = {
        'all_drop_in': lambda e: True,
        'drop_in': lambda e: True,
        'any': lambda e: True,
        'stick_n_puck': lambda e: True,
    }


class Kent(Google):
    rink = "Kent"
    location = "Kent Valley Ice Centre"
    snp_id = "kentvalleyicecentre.com@gmail.com"

    filters = {
        'all_drop_in': lambda e: "Stick" in e.summary,
        'drop_in': lambda e: "Stick" in e.summary,
        'any': lambda e: True,
        'stick_n_puck': lambda e: "Stick" in e.summary,
    }


class SnoKing(Rink):
    location = "SnoKing"

    filters = {
        'any': lambda e: True,
        'stick_n_puck': lambda e: "Stick" in e['eventName'],
        'all_drop_in': lambda e: ("Drop" in e['eventName'] \
                             or "Stick" in e['eventName']) \
                             and not "Invite" in e['eventName'],
        'drop_in': lambda e: "Drop" in e['eventName'] \
                             and not "Invite" in e['eventName'],
        'public': lambda e: "Public" in e['eventName']
    }

    def _events(self):
        start = self.start.strftime('%Y-%m-%d')
        end = self.end.strftime('%Y-%m-%d')
        return requests.get(f'https://api.bondsports.co/v3/facilities/{self.api_id}/programs-schedule?startDate={start}&endDate={end}').json()['data']

    def _truncate_name(self, e):
        try:
            return e['eventName'][:e['eventName'].index('Stick N Puck')+12].replace(' - ', ' ')
        except ValueError:
            return e['eventName']

    def to_gcal(self, e):
        name = self._truncate_name(e)
        if not name.upper().startswith(self.rink.upper()):
            name = self.rink + ' ' + name
        location = self.location
        if len(e['spaces']) > 0:
            sheet = e['spaces'][0]['spaceName']
            location = self.location + ' '  + sheet
        start = self._parse_date(e['eventStartDate'] + ' ' + e['eventStartTime'])
        end = self._parse_date(e['eventStartDate'] + ' ' + e['eventEndTime'])
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


class WISA(Rink):
    filters = {
        'stick_n_puck': lambda e: "Stick" in e['title'],
        'drop_in': lambda e: "Drop" in e['title'] or "Lunch" in e['title'],
        'all_drop_in': lambda e: "Stick" in e['title'] or "Drop" in e['title'] or "Lunch" in e['title']
    }

    def _events(self):
        start = self.start.strftime('%Y-%m-%d')
        end = self.end.strftime('%Y-%m-%d')
        # multiview=1 returns events for both rinks, but Lynnwood event
        # objects don't indicate their location.
        return requests.get(f'https://www.rectimes.app/ova/booking/getbooking?rink={self.api_id}&multiview=0&minstart=06:00:00&maxend=26:00:00&start={start}&end={end}&_=1680859722270').json()

    def to_gcal(self, e):
        name = e['title']
        if not name.upper().startswith(self.rink.upper()):
            name = self.rink + ' ' + name
        start = self._parse_date(e['start'])
        end = self._parse_date(e['end'])
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


class KCI(Rink):
    rink = "KCI"
    location = "Kraken Community Iceplex"

    filters = {
        'hockey': lambda e: e['sportId'] == 20,
        'stick_n_puck': lambda e: "Stick" in e['title'],
        'drop_in': lambda e: "Drop" in e['title'],
        'all_drop_in': lambda e: "Stick" in e['title'] or "Drop" in e['title']
    }

    def _parse_date(self, date):
        return dateutil_parse(date).replace(tzinfo=UTC)

    def _events(self):
        start = self.start.strftime('%Y-%m-%d')
        end = self.end.strftime('%Y-%m-%d')
        return requests.get(f'https://www.krakencommunityiceplex.com/Umbraco/api/DaySmartCalendarApi/GetEventsAsync?start={start}&end={end}&variant=2').json()

    def _truncate_name(self, name):
        # Handle "Drop-in GOALIE" and "Drop-In SKATER" describing two links
        # for the same event.
        try:
            return name[:name.upper().index('DROP-IN')+7].upper()
        except ValueError:
            return name

    def to_gcal(self, e):
        name = self._truncate_name(e['title'])
        if not name.upper().startswith(self.rink.upper()):
            name = self.rink + ' ' + name
        start = self._parse_date(e['start'])
        end = self._parse_date(e['end'])
        print(f'Creating Event({name}, {start}, {end}, {self.location})')
        return Event(name, start=start, end=end, location=self.location)
