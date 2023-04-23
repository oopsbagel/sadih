import os
from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event

sadih = GoogleCalendar(os.environ['SADIH_ID'])
for e in sadih:
    sadih.delete_event(e)
