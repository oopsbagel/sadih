#!/usr/bin/env python3

from collections import defaultdict
from dateutil.parser import parse as dateutil_parse
from functools import partial
from os import environ
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar

from rinks import *

START = '2023-06-28'
END = '2023-08-01'
start = dateutil_parse(START).replace(tzinfo=PACIFIC)
end = dateutil_parse(END).replace(tzinfo=PACIFIC)

rinks = [Everett, Kirkland, Renton, Snoqualmie, OVA, Lynnwood, KCI, Kent]

def calendar(gcal_id, rinks, event_filter_name, start, end):
    sadih = GoogleCalendar(environ['SADIH_ID'])

    existing_events_by_rink = defaultdict(list)
    for e in sadih.get_events(start, end):
        name = e.summary.split(" ")[0]
        existing_events_by_rink[name].append(e)

    created_events = []
    removed_events = []

    for rink in rinks:
        response_events = combine_like_events(rink(start, end).gcal(event_filter_name))
        existing_events = existing_events_by_rink[rink.rink]
        print(f"{rink.location} existing events")
        for e in existing_events:
            print(e)

        print(f"{rink.location} removed events")
        for e in subtract_events(existing_events, response_events):
            print(e)
            removed_events.append(e)

        print(f"{rink.location} new events")
        for e in subtract_events(response_events, existing_events):
            print(e)
            created_events.append(e)

    for e in removed_events:
        print('[-] deleting', e)
        sadih.delete_event(e)

    for e in created_events:
        print('[+] adding', e)
        sadih.add_event(e)

calendar(environ['SADIH_ID'], rinks, 'drop_in', start, end)
