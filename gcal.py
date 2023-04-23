#!/usr/bin/env python3

import os
import itertools
from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event

from rinks import *

START = '2023-04-22'
END = '2023-04-30'

sadih = GoogleCalendar(os.environ['SADIH_ID'])

#for e in Kirkland(START, END).gcal('drop_in'):
#for e in Snoqualmie(START, END).gcal('stick_n_puck'):
    #sadih.add_event(e)

r = []
#r = r + list(Renton(START, END).gcal('drop_in'))
#r = r + list(Snoqualmie(START, END).gcal('drop_in'))
#r = r + list(Kirkland(START, END).gcal('drop_in'))
#r = r + list(OVA(START, END).gcal('drop_in'))
#r = r + list(Lynnwood(START, END).gcal('drop_in'))
r = r + list(KCI(START, END).gcal('drop_in'))

i = 0
while i+1 < len(r):
    if events_are_abutting(r[i], r[i+1]):
        print(f"{r[i]} and {r[i+1]} found to be the same")
        r = r[:i] + [merge_events(r[i], r[i+1])] + r[i+2:]
    else:
        i = i + 1

for e in r:
    sadih.add_event(e)
    print(e, e.start, e.end)

print("the calendar now:")
for e in sadih:
    print(e)
