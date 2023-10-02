import functions_framework
from calendars import main
from datetime import timedelta

@functions_framework.cloud_event
def cloudevent_main(cloud_event):
    until = timedelta(weeks=4)
    main('config.yaml', until)

cloudevent_main(None)
