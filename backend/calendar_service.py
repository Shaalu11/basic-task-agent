from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from datetime import datetime, timedelta


def get_calendar_service(token):
    creds = Credentials.from_authorized_user_info(token)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build('calendar', 'v3', credentials=creds)
    return service


# ✅ ADD EVENT
def add_event(token, title, date, time, end_time=None):
    service = get_calendar_service(token)

    start_datetime = f"{date}T{time}:00"

    if end_time:
        end_datetime = f"{date}T{end_time}:00"
    else:
        try:
            parsed_start = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            parsed_end = parsed_start + datetime.timedelta(hours=1)
            end_datetime = parsed_end.strftime("%Y-%m-%dT%H:%M:%S")
        except Exception:
            end_datetime = f"{date}T{time}:59"

    event = {
        'summary': title,
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'Asia/Kolkata'
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': 'Asia/Kolkata'
        },
    }

    service.events().insert(calendarId='primary', body=event).execute()
    return {"message": "Event added successfully"}


# ✅ DELETE EVENT
def delete_event(token, title):
    service = get_calendar_service(token)

    events_result = service.events().list(
        calendarId='primary',
        q=title,
        maxResults=5,
        singleEvents=True
    ).execute()

    events = events_result.get('items', [])

    for event in events:
        if event['summary'].lower() == title.lower():
            service.events().delete(
                calendarId='primary',
                eventId=event['id']
            ).execute()
            return {"message": "Event deleted"}

    return {"message": "Event not found"}


# ✅ RESCHEDULE EVENT
def reschedule_event(token, title, new_date=None, new_time=None):
    service = get_calendar_service(token)

    events_result = service.events().list(
        calendarId='primary',
        q=title,
        maxResults=5,
        singleEvents=True
    ).execute()

    events = events_result.get('items', [])

    for event in events:
        if event['summary'].lower() == title.lower():

            old_start = event['start']['dateTime']

            date_part = old_start[:10]
            time_part = old_start[11:16]

            if new_date:
                date_part = new_date
            if new_time:
                time_part = new_time

            updated_event = {
                'summary': event['summary'],
                'start': {
                    'dateTime': f"{date_part}T{time_part}:00",
                    'timeZone': 'Asia/Kolkata'
                },
                'end': {
                    'dateTime': f"{date_part}T{time_part}:59",
                    'timeZone': 'Asia/Kolkata'
                },
            }

            service.events().update(
                calendarId='primary',
                eventId=event['id'],
                body=updated_event
            ).execute()

            return {"message": "Event rescheduled"}

    return {"message": "Event not found"}