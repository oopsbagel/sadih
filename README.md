# Seattle Area Drop In Hockey Calendar

Scrape rink calendars for Stick & Puck and other Drop In Hockey events and upload to Google Calendar.

[Google Calendar](https://calendar.google.com/calendar/embed?src=seattleareadropinhockey%40gmail.com&ctz=America%2FLos_Angeles)

Supports the following rinks:
- [Everett Angel of the Winds Arena](https://www.angelofthewindsarena.com/ice-rink/ice-rink-calendar)
- [Kent Valley Ice Centre](https://www.angelofthewindsarena.com/ice-rink/ice-rink-calendar)
- [Northgate Kraken Community Iceplex](https://www.krakencommunityiceplex.com/public-drop-in-calendar/)
- [Lynnwood Ice Arena](https://www.rectimes.app/ova/cat/lic)
- [Olympic View Arena](https://www.rectimes.app/ova/cat/ova)
- [SnoKing Kirkland](https://bondsports.co/org/209/225/schedule)
- [SnoKing Renton](https://bondsports.co/org/209/255/schedule)
- [SnoKing Snoqualmie](https://bondsports.co/org/209/256/schedule)

Please report any problems here.

## A note

Yes, this is brittle. It relies on implementation details of upstream calendars, and it breaks [djb's 5th design principal, "don't parse"](http://cr.yp.to/qmail/guarantee.html). Nevertheless, I think it is useful.
