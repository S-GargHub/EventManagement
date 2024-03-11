import pytz

from datetime import datetime, time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_calender_events(credentials, start_date, end_date):
    try:
        # Call the Calendar API
        service = build("calendar", "v3", credentials=credentials)
        start = datetime.combine(start_date, time.min).isoformat() + "Z"  # 'Z' indicates UTC time
        end = datetime.combine(end_date, time.min) + "Z"  # 'Z' indicates UTC time
        
        events_query = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start,
                timeMax=end,
                maxResults=15,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events_result = events_query.get("items", [])
        events = []

        if not events_result:
            events.append("No upcoming events found in the calendar.")
        else:
            for event in events_result:
                start = event["start"].get("dateTime", event["start"].get("date"))
                event_time = (
                    datetime.fromisoformat(start)
                    .astimezone(pytz.timezone("Asia/Kolkata"))
                    .strftime("%Y-%m-%d %H:%M:%S")
                )
                events.append(f"{event_time} - {event['summary']}")

    except HttpError as e:
        print(f"An error occurred: {e}")

    return events_result