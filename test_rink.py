import pytest
import json
from dateutil.parser import parse as parse_date

from rinks import *

class FakeKirkland(Kirkland):
    def _json_events(self):
        with open('fixture_kirkland.json') as f:
            return json.load(f)['data']

class FakeSnoqualmie(Snoqualmie):
    def _json_events(self):
        with open('fixture_snoqualmie.json') as f:
            return json.load(f)['data']

class FakeRenton(Renton):
    def _json_events(self):
        with open('fixture_renton.json') as f:
            return json.load(f)['data']

def test_event():
    events = FakeKirkland('2023-04-20', '2023-04-21').gcal('stick_n_puck')
    events = list(events)
    assert len(events) == 1
    expected_event = Event(
        "Kirkland Stick N Puck",
        start=parse_date("2023-04-20 11:30:00"),
        end=parse_date("2023-04-20 12:30:00"),
        location="SnoKing Kirkland Rink")
    assert events[0].summary == expected_event.summary
    assert events[0].start == expected_event.start
    assert events[0].end == expected_event.end
    assert events[0].location == expected_event.location
    assert events_are_same(events[0], expected_event)

def test_any_filter():
    events = FakeKirkland('2023-04-20', '2023-04-21').gcal('any')
    events = list(events)
    assert len(events) == 18

def test_combine_like_events():
    events = FakeRenton('2023-04-20', '2023-04-21').gcal('stick_n_puck')
    events = list(events)
    assert len(events) == 6
    events = combine_like_events(events)
    assert len(events) == 3

def test_new_events():
    events = FakeKirkland('2023-04-20', '2023-04-21').gcal('any')
    events = list(events)
    excluded_event = events[0]
    existing_events = events[1:]
    assert [excluded_event] == subtract_events(events, existing_events)

def test_delete_events():
    events = FakeKirkland('2023-04-20', '2023-04-21').gcal('any')
    events = list(events)
    excluded_event = events[0]
    existing_events = events
    assert [excluded_event] == subtract_events(existing_events, events[1:])
