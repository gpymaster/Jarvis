"""
JARVIS Calendar Integration Module
Provides voice-friendly calendar operations
"""

from __future__ import print_function
import datetime
import os
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import dateutil.parser
import dateutil.tz
import json
import re
import pytz

# Add google_ai to path
sys.path.append('/Users/graysonkeenan/Desktop/Jarvis/google docs assces')
from google_ai import ask_ai_chat

# Scopes for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarManager:
    def __init__(self):
        self.service = self._authenticate()
        self.timezone = 'America/Los_Angeles'

    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        token_path = '/Users/graysonkeenan/Desktop/Jarvis/google docs assces/token.pickle'
        creds_path = '/Users/graysonkeenan/Desktop/Jarvis/google docs assces/google_calender_passkey.json'

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        return build('calendar', 'v3', credentials=creds)

    def get_events(self, days_ahead=3, include_past_hour=True):
        """Get events from all calendars"""
        now = datetime.datetime.now(datetime.timezone.utc)

        if include_past_hour:
            time_min = (now - datetime.timedelta(hours=1)).isoformat()
        else:
            time_min = now.isoformat()

        time_max = (now + datetime.timedelta(days=days_ahead)).isoformat()

        # Get all calendars
        calendar_list = self.service.calendarList().list().execute()
        calendar_ids = [cal['id'] for cal in calendar_list['items']]

        # Fetch events from all calendars
        all_events = []
        for calendar_id in calendar_ids:
            try:
                events_result = self.service.events().list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()

                events = events_result.get('items', [])
                for event in events:
                    event['calendar_id'] = calendar_id
                    all_events.append(event)
            except Exception as e:
                print(f"Error fetching events from calendar {calendar_id}: {e}")

        # Sort by start time
        all_events.sort(key=lambda e: self._get_start_time(e))

        return all_events

    def _parse_event_time(self, event_time):
        """Parse event time string to datetime"""
        dt = dateutil.parser.isoparse(event_time)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=dateutil.tz.UTC)
        return dt

    def _get_start_time(self, event):
        """Get start time from event"""
        return self._parse_event_time(
            event['start'].get('dateTime', event['start'].get('date'))
        )

    def get_today_summary(self):
        """Get a summary of today's events"""
        events = self.get_events(days_ahead=1, include_past_hour=True)
        now = datetime.datetime.now(datetime.timezone.utc)
        today = now.date()

        today_events = []
        for event in events:
            start = self._get_start_time(event)
            if start.date() == today:
                today_events.append(event)

        if not today_events:
            return "You have no events scheduled for today."

        # Format events for AI summary
        event_list = []
        for event in today_events:
            start = self._get_start_time(event)
            end = self._parse_event_time(event['end'].get('dateTime', event['end'].get('date')))

            event_info = {
                "title": event.get('summary', 'Untitled'),
                "start": start.strftime('%I:%M %p'),
                "end": end.strftime('%I:%M %p'),
                "status": "ongoing" if start <= now <= end else "upcoming" if start > now else "past"
            }
            event_list.append(event_info)

        calendar_data = json.dumps(event_list, indent=2)
        summary = ask_ai_chat(
            f"From this calendar data: {calendar_data}, create a brief summary of what I have scheduled today. "
            f"Keep it conversational and concise (2-3 sentences max)."
        )

        return summary

    def get_upcoming_events_text(self, count=5):
        """Get upcoming events as readable text"""
        events = self.get_events(days_ahead=7)
        now = datetime.datetime.now(datetime.timezone.utc)

        upcoming = [e for e in events if self._get_start_time(e) > now][:count]

        if not upcoming:
            return "No upcoming events found."

        result = []
        for event in upcoming:
            start = self._get_start_time(event)
            summary = event.get('summary', 'Untitled Event')

            # Format date
            if start.date() == datetime.datetime.now().date():
                date_str = "Today"
            elif start.date() == (datetime.datetime.now() + datetime.timedelta(days=1)).date():
                date_str = "Tomorrow"
            else:
                date_str = start.strftime('%A, %B %d')

            time_str = start.strftime('%I:%M %p')

            result.append(f"{summary} on {date_str} at {time_str}")

        return "Your upcoming events are: " + "; ".join(result)

    def create_event_from_text(self, user_request):
        """Create a calendar event from natural language"""
        events = self.get_events(days_ahead=7)
        now = datetime.datetime.now(datetime.timezone.utc)

        # Format existing events
        event_list = []
        for event in events:
            start = self._get_start_time(event)
            end = self._parse_event_time(event['end'].get('dateTime', event['end'].get('date')))

            event_list.append({
                "title": event.get('summary', ''),
                "start": start.isoformat(),
                "end": end.isoformat()
            })

        calendar_data = json.dumps(event_list, indent=2)

        # Ask AI to create event details
        prompt = f'''Based on my calendar: {calendar_data}

User request: "{user_request}"

Create an event in JSON format with these exact keys:
{{
  "summary": "Title with 'Grayson -' prefix",
  "description": "Event description",
  "start_time": "ISO format in America/Los_Angeles timezone",
  "end_time": "ISO format in America/Los_Angeles timezone"
}}

Find a good time that doesn't conflict. Use California time.
Only output valid JSON. No code blocks, no explanation.'''

        response = ask_ai_chat(prompt)

        # Clean response
        json_str = re.sub(r'```json|```', '', response).strip()

        try:
            data = json.loads(json_str)

            # Parse times
            start_dt = dateutil.parser.isoparse(data['start_time']).astimezone(
                pytz.timezone(self.timezone)
            )
            end_dt = dateutil.parser.isoparse(data['end_time']).astimezone(
                pytz.timezone(self.timezone)
            )

            # Create the event
            event = {
                'summary': data['summary'],
                'description': data.get('description', ''),
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': self.timezone,
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': self.timezone,
                }
            }

            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            return f"Event created: {data['summary']} on {start_dt.strftime('%A at %I:%M %p')}"

        except json.JSONDecodeError as e:
            return f"Error parsing AI response: {e}"
        except Exception as e:
            return f"Error creating event: {e}"

    def get_next_event(self):
        """Get the next upcoming event"""
        events = self.get_events(days_ahead=7)
        now = datetime.datetime.now(datetime.timezone.utc)

        for event in events:
            start = self._get_start_time(event)
            if start > now:
                summary = event.get('summary', 'Untitled Event')
                time_str = start.strftime('%I:%M %p')

                if start.date() == datetime.datetime.now().date():
                    return f"Your next event is {summary} at {time_str} today"
                elif start.date() == (datetime.datetime.now() + datetime.timedelta(days=1)).date():
                    return f"Your next event is {summary} tomorrow at {time_str}"
                else:
                    date_str = start.strftime('%A, %B %d')
                    return f"Your next event is {summary} on {date_str} at {time_str}"

        return "No upcoming events found"


# Simple function wrappers for voice commands
def get_calendar_summary():
    """Get today's calendar summary"""
    cal = CalendarManager()
    return cal.get_today_summary()

def get_upcoming_events():
    """Get upcoming events"""
    cal = CalendarManager()
    return cal.get_upcoming_events_text()

def create_calendar_event(request):
    """Create event from natural language"""
    cal = CalendarManager()
    return cal.create_event_from_text(request)

def get_next_event():
    """Get next event"""
    cal = CalendarManager()
    return cal.get_next_event()


if __name__ == "__main__":
    # Test
    cal = CalendarManager()
    print(cal.get_today_summary())
