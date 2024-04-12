import pytz

from datetime import datetime, time, timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_events(credentials, start_date, end_date):
    try:
        # Call the Calendar API
        service = build("calendar", "v3", credentials=credentials)
        start = datetime.combine(start_date, time.min).replace(tzinfo=timezone.utc).isoformat() 
        end = datetime.combine(end_date, time.min).replace(tzinfo=timezone.utc).isoformat()
        
        events_query = service.events().list(
                calendarId="primary",
                timeMin=start,
                timeMax=end,
                maxResults=15,
                singleEvents=True,
                orderBy="startTime",
            ).execute()

        events_result = events_query.get("items", [])
        events = []

        if not events_result:
            events.append("No upcoming events found in the calendar.")
        else:
            for event in events_result:
                start = event['start'].get('dateTime', event['start'].get('date'))
                start_time = datetime.fromisoformat(start)
                event_time = start_time.strftime('%Y-%m-%d %H:%M')
                event_info = {
                    'id': event['id'],
                    'summary': event['summary'],
                    'time': event_time
                }
                events.append(event_info)

    except HttpError as e:
        print(f"An error occurred: {e}")

    return events

# def delete_events(credentials):
#     try:
#         # Delete the event
#         calendar_service = build('calendar', 'v3', credentials=credentials)
#         calendar_service.events().delete(calendarId="primary", eventId=EVENT_ID).execute()
#         print(f'Event with ID {EVENT_ID} has been deleted.')
#     except Exception as e:
#         print(f'An error occurred: {e}')


def create_event(credentials, summary, start_date, end_date):
    """
    Creates a new calendar event.

    Args:
        summary (str): The title of the event.
        start_date (datetime): The start date and time of the event.
        end_date (datetime): The end date and time of the event.
    """
    # Create a Google Calendar API client
    calendar_service = build('calendar', 'v3', credentials=credentials)
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_date.isoformat(),
            'timeZone': "UTC",
        },
        'end': {
            'dateTime': end_date.isoformat(),
            'timeZone': "UTC",
        },
    }

    try:
        event = calendar_service.events().insert(calendarId="primary", body=event).execute()
    except Exception as e:
        print(f'An error occurred: {e}')
    return event