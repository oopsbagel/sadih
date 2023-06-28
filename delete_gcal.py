import os
from dateutil.parser import parse as dateutil_parse
from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event
from zoneinfo import ZoneInfo

PACIFIC = ZoneInfo("America/Los_Angeles")

START = '2023-06-14'
END = '2023-06-17'

start_dt = dateutil_parse(START).replace(tzinfo=PACIFIC)
end_dt = dateutil_parse(END).replace(tzinfo=PACIFIC)

sadih = GoogleCalendar(os.environ['SADIH_ID'])
for e in sadih.get_events(start_dt, end_dt):
    sadih.delete_event(e)
