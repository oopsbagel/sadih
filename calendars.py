from gcsa.calendar import Calendar
from gcsa.google_calendar import GoogleCalendar
from os import environ

DESCRIPTION = """
Seattle Area Drop In Hockey Calendar
https://github.com/oopsbagel/sadih
"""

gc = GoogleCalendar()

def make_kirkland():
    cal = Calendar('Kirkland')
    gc.add_calendar(cal)

sadih = GoogleCalendar(environ['SADIH_ID'])

for c in gc.get_calendar_list():
    print(c, c.id)
