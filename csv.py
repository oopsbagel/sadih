#!/usr/bin/env python3

from rinks import *

# https://support.google.com/calendar/answer/37118?hl=en&co=GENIE.Platform%3DDesktop#zippy=%2Ccreate-or-edit-a-csv-file
print(CSV_HEADER)

START = '2023-04-17'
END = '2023-04-24'

start = "2023-04-17T00:00:00-07:00"
end = "2023-04-24T00:00:00-07:00"

print(Renton(START, END).csv('drop_in'))
#print(Snoqualmie(START, END).csv('stick_n_puck'))
#print(calendar(Kirkland, 'public', START, END))
#print(calendar(Kirkland, 'stick_n_puck', START, END))
#print(calendar(Renton, 'stick_n_puck', START, END))
#print(calendar(Snoqualmie, 'stick_n_puck', START, END))
print(OVA(start, end).csv('stick_n_puck'))
print(Lynnwood(start, end).csv('stick_n_puck'))
print(KCI(start, end).csv('stick_n_puck'))
