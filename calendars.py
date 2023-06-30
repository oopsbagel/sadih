#!/usr/bin/env python3

from collections import defaultdict
from datetime import datetime, timedelta
from gcsa.google_calendar import GoogleCalendar
from yaml import safe_load

from rinks import *

def update_calendar(gcal_id, rinks, event_filter_name, start, end):
    sadih = GoogleCalendar(gcal_id)

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

def sync_calendars(config_path):
    with open(config_path) as file:
        conf = safe_load(file)

    tomorrow = datetime.now(tz=PACIFIC) + timedelta(days=1)
    four_weeks = tomorrow + timedelta(weeks=4)

    for cal_name in conf['calendars']:
        cal = conf['calendars'][cal_name]
        cal_rinks = map(lookup_rink, cal['rinks'])
        print(cal['id'], cal_rinks, cal['filter'], tomorrow, four_weeks)
        update_calendar(cal['id'], cal_rinks, cal['filter'], tomorrow, four_weeks)

if __name__ == '__main__':
    import sys
    config_path = 'config.yaml'
    if len(sys.argv) == 2:
        config_path = sys.argv[1]
    sync_calendars(config_path)
