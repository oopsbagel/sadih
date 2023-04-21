#!/usr/bin/env python3

from rinks import CSV_HEADER, Kirkland

# https://support.google.com/calendar/answer/37118?hl=en&co=GENIE.Platform%3DDesktop#zippy=%2Ccreate-or-edit-a-csv-file
print(CSV_HEADER)

START = '2023-04-17'
END = '2023-04-24'

start = "2023-04-01T00:00:00-07:00"
end = "2023-04-08T00:00:00-07:00"

print(Kirkland(START, END).csv('stick_n_puck'))
#print(calendar(Kirkland, 'public', START, END))
#print(calendar(Kirkland, 'stick_n_puck', START, END))
#print(calendar(Renton, 'stick_n_puck', START, END))
#print(calendar(Snoqualmie, 'stick_n_puck', START, END))
#print(calendar(OVA, 'stick_n_puck', start, end))
#print(calendar(Lynnwood, 'stick_n_puck', start, end))
#print(calendar(KCI, 'stick_n_puck', start, end))
