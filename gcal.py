#!/usr/bin/env python3

from collections import defaultdict
from dateutil.parser import parse as dateutil_parse
from functools import partial
from os import environ
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar

from rinks import *

START = '2023-06-06'
END = '2023-07-31'

start_dt = dateutil_parse(START).replace(tzinfo=PACIFIC)
end_dt = dateutil_parse(END).replace(tzinfo=PACIFIC)

sadih = GoogleCalendar(environ['SADIH_ID'])

rinks = [Everett, Kirkland, Renton, Snoqualmie, OVA, Lynnwood, KCI]

existing_locations = defaultdict(list)
for e in sadih.get_events(start_dt, end_dt):
    existing_locations[e.location].append(e)

for rink in rinks:
    response_events = combine_like_events(rink(START, END).gcal('drop_in'))
    existing_events = existing_locations[rink.location]
    print(f"{rink.location} existing events")
    for e in existing_events:
        print(e)

    print(f"{rink.location} removed events")
    for e in subtract_events(existing_events, response_events):
        print('[-] deleting', e)
        sadih.delete_event(e)

    print(f"{rink.location} new events")
    for e in subtract_events(response_events, existing_events):
        print('[+] adding', e)
        sadih.add_event(e)

print("the calendar now")
for e in sadih:
    print(e)
