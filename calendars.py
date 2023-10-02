#!/usr/bin/env python3

from collections import defaultdict
from datetime import datetime, timedelta
from gcsa.google_calendar import GoogleCalendar
from yaml import safe_load

from rinks import *

all_rinks = [Everett, Kirkland, Renton, Snoqualmie, OVA, Lynnwood, KCI, Kent]

def lookup_rink(rink_name):
    """ Return Rink object with matching name """
    for rink in all_rinks:
        if rink_name == rink.rink:
            return rink
    raise RuntimeError(f"rink {rink_name} not found")

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

def sync_calendars(calendars, until):
    tomorrow = datetime.now(tz=PACIFIC) + timedelta(days=1)
    end_date = tomorrow + until
    for cal in calendars:
        update_calendar(*cal, tomorrow, end_date)

def load_config(config_path):
    with open(config_path) as file:
        config = safe_load(file)
    calendars = []
    for cal in config['calendars'].values():
        rinks = list(map(lookup_rink, cal['rinks']))
        print(cal['id'], rinks, cal['filter'])
        calendars.append([cal['id'], rinks, cal['filter']])
    return calendars

CONFIG_TEMPLATE = """
calendars:
  calendar_name:
    id: gcal_id@group.calendar.google.com
    rinks: [Kirkland, Snoqualmie, Renton]
    filter: drop_in"""

def main(config_path, until):
    try:
        calendars = load_config(config_path)
    except (KeyError, TypeError):
        raise ValueError(f"config must follow format:\n{CONFIG_TEMPLATE}")
    sync_calendars(calendars, until)

if __name__ == '__main__':
    import sys
    config_path = 'config.yaml'
    if len(sys.argv) == 2:
        config_path = sys.argv[1]
    until = timedelta(weeks=4)
    main(config_path, until)
