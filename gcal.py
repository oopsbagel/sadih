#!/usr/bin/env python3

import itertools
from dateutil.parser import parse as dateutil_parse
from functools import partial
from os import environ
from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event

from rinks import *

START = '2023-04-28'
END = '2023-05-07'

start = dateutil_parse(START).replace(tzinfo=TIMEZONE)
end = dateutil_parse(END).replace(tzinfo=TIMEZONE)

sadih = GoogleCalendar(environ['SADIH_ID'])

r = []
r = r + list(Renton(START, END).gcal('drop_in'))
r = r + list(Snoqualmie(START, END).gcal('drop_in'))
r = r + list(Kirkland(START, END).gcal('drop_in'))
r = r + list(OVA(START, END).gcal('drop_in'))
r = r + list(Lynnwood(START, END).gcal('drop_in'))
r = r + list(KCI(START, END).gcal('drop_in'))

response_events = combine_like_events(r)

existing_events = list(sadih.get_events(start, end))

print("existing events")
for e in existing_events:
    print(e)

print("removed events")
for e in subtract_events(existing_events, response_events):
    print('[-] deleting', e)
    sadih.delete_event(e)

print("new events")
for e in subtract_events(response_events, existing_events):
    print('[+] adding', e)
    sadih.add_event(e)

print("the calendar now")
for e in sadih:
    print(e)
