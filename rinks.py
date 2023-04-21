#!/usr/bin/env python3

import requests
from functools import partial
from itertools import chain

CSV_HEADER = "Subject, Start date, Start time, End time, Location"

class Facility:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def csv(f, event_filter):
        return "\n".join(map(f.to_csv, filter(f.filters[event_filter], f.events())))

class SnoKing(Facility):
    location = "SnoKing"

    filters = {
        'stick_n_puck': lambda e: "Stick" in e['eventName'],
        'public': lambda e: "Public" in e['eventName']
    }

    def events(self):
        return requests.get(f'https://api.bondsports.co/v3/facilities/{self.api_id}/programs-schedule?startDate={self.start}&endDate={self.end}').json()['data']
    
    def to_csv(self, e):
        name = self.rink + ' ' + e['eventName']
        location = self.location
        if len(e['spaces']) > 0:
            sheet = e['spaces'][0]['spaceName']
            location = self.location + ' '  + sheet
        return ", ".join([name, e['eventStartDate'], e['eventStartTime'], e['eventEndTime'], location])

class Kirkland(SnoKing):
    api_id = 225
    rink = "KIRK"

class Renton(SnoKing):
    api_id = 255
    rink = "RENT"

class Snoqualmie(SnoKing):
    api_id = 256
    rink = "SNOQ"

class WISA(Facility):
    filters = {
        'stick_n_puck': lambda e: "Stick" in e['title']
    }

    def events(self):
        # multiview=1 returns events for both rinks, but Lynnwood event
        # objects don't indicate their location.
        return requests.get(f'https://www.rectimes.app/ova/booking/getbooking?rink={self.api_id}&multiview=0&minstart=06:00:00&maxend=26:00:00&start={self.start}&end={self.end}&_=1680859722270').json()

    def to_csv(self, e):
        name = e['title']
        if not e['title'].startswith(self.rink):
            name = self.rink + ' ' + name
        date, start = e['start'].split(' ')
        _, end = e['end'].split(' ')
        return ", ".join([name, date, start, end, self.location])

class OVA(WISA):
    api_id = 1145
    rink = "OVA"
    location = "Olympic View Arena"

class Lynnwood(WISA):
    api_id = 1146
    rink = "LYNN"
    location = "Lynnwood Ice Center"

class KCI(Facility):
    rink = "KCI"
    location = "Kraken Community Iceplex"

    filters = {
        'hockey': lambda e: e['sportId'] == 20,
        'stick_n_puck': lambda e: "Stick" in e['title']
    }

    def events(self):
        return requests.get(f'https://www.krakencommunityiceplex.com/Umbraco/api/DaySmartCalendarApi/GetEventsAsync?start={self.start}&end={self.end}&variant=2').json()

    def to_csv(self, e):
        name = self.rink + ' ' + e['title']
        date, start = e['start'].split('T')
        _, end = e['end'].split('T')
        return ", ".join([name, date, start[:-1], end[:-1], self.location])
