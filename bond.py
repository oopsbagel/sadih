#!/usr/bin/env python3

import requests
from functools import partial
from itertools import chain

START = '2023-04-14'
END = '2023-04-15'

class Facility:
    pass

class SnoKing(Facility):
    RENTON = 255
    KIRKLAND = 225
    SNOQUALMIE = 256

    stick_n_puck_filter = lambda e: "Stick" in e['eventName']

    @staticmethod
    def events(rink):
        return requests.get(f'https://api.bondsports.co/v3/facilities/{rink}/programs-schedule?startDate={START}&endDate={END}').json()['data']
    
    @staticmethod
    def format_event(e):
        # https://support.google.com/calendar/answer/37118?hl=en&co=GENIE.Platform%3DDesktop#zippy=%2Ccreate-or-edit-a-csv-file
        name = e['eventName']
        if len(e['spaces']) > 0:
            sheet = e['spaces'][0]['spaceName']
            name = sheet + ' ' + name
        print(", ".join([name, e['eventStartDate'], e['eventStartTime'], e['eventEndTime']]))

class OvaLynn(Facility):
    OlympicView = 1145
    Lynnwood = 1146

    START = '2023-04-12T00:00:00-07:00'
    END = '2023-04-13T00:00:00-07:00'

    stick_n_puck_filter = lambda e: "Stick" in e['eventType']

    @staticmethod
    def events(rink, start, end):
        # multiview=1 returns events for both rinks, but Lynnwood event
        # objects don't indicate their location.
        return requests.get(f'https://www.rectimes.app/ova/booking/getbooking?rink={rink}&multiview=0&minstart=06:00:00&maxend=26:00:00&start={start}&end={end}&_=1680859722270').json()

    @staticmethod
    def format_event(e):
        name = e['title']
        date, start = e['start'].split(' ')
        _, end = e['end'].split(' ')
        return ", ".join([name, date, start, end])

class Lynnwood(OvaLynn):
    address = "123 Main St"
    api_id = 1146

    @staticmethod
    def format_event(e):
        return "Lynnwood " + super().format_event(e)

def calendar(events, _filter, formatter):
    return map(formatter, filter(_filter, events()))

snoking = calendar(lambda: chain(*map(SnoKing.events, [SnoKing.KIRKLAND, SnoKing.RENTON, SnoKing.SNOQUALMIE])), SnoKing.stick_n_puck_filter, SnoKing.format_event)

CSV_HEADER = "Subject, Start date, Start time, End time, Location"
print(CSV_HEADER)
list(snoking)

o = OvaLynn.events(OvaLynn.OlympicView, OvaLynn.START, OvaLynn.END)
l = OvaLynn.events(OvaLynn.Lynnwood, OvaLynn.START, OvaLynn.END)
#list(map(OvaLynn.format_event, filter(OvaLynn.stick_n_puck_filter, o)))
#print("\n".join(map(partial(OvaLynn.format_event, "Olympic View Arena"), o)))
print("\n".join(map(OvaLynn.format_event, o)))
#print("\n".join(map(OvaLynn.format_event, o)))
#print("\n".join(map(lambda e: "Lynnwood " + e, map(partial(OvaLynn.format_event, "Lynnwood Ice Center"), l))))
