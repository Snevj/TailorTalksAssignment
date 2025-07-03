import os
import json
from datetime import datetime, timedelta
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import List, Dict, Optional

class GoogleCalendarService:
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.service = self._initialize_service()
        
    def _initialize_service(self):
        """Initialize Google Calendar API service"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            service = build('calendar', 'v3', credentials=credentials)
            return service
        except Exception as e:
            print(f"Error initializing calendar service: {e}")
            raise Exception(f"Failed to initialize Google Calendar service: {e}")

    
    def get_calendar_list(self):
        """Get list of available calendars"""
        try:
            calendar_list = self.service.calendars().list().execute()
            return calendar_list.get('items', [])
        except Exception as e:
            print(f"Error getting calendar list: {e}")
            return []
    
    def check_availability(self, start_time: datetime, end_time: datetime, calendar_id: str = 'primary') -> bool:
        """Check if a time slot is available"""
        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return len(events) == 0
        except Exception as e:
            print(f"Error checking availability: {e}")
            return False
    
    def get_available_slots(self, date: datetime, duration_minutes: int = 60, 
                          start_hour: int = 9, end_hour: int = 17, 
                          calendar_id: str = 'primary') -> List[Dict]:
        """Get available time slots for a given date"""
        available_slots = []
        
        # Set timezone
        tz = pytz.timezone('UTC')  # You can change this to your timezone
        
        # Create datetime objects for the start and end of business hours
        start_of_day = date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        
        current_time = start_of_day
        slot_duration = timedelta(minutes=duration_minutes)
        
        while current_time + slot_duration <= end_of_day:
            end_time = current_time + slot_duration
            
            if self.check_availability(current_time, end_time, calendar_id):
                available_slots.append({
                    'start': current_time.isoformat(),
                    'end': end_time.isoformat(),
                    'formatted_time': current_time.strftime('%I:%M %p')
                })
            
            current_time += timedelta(minutes=30)  # Check every 30 minutes
        
        return available_slots
    
    def book_appointment(self, title: str, description: str, start_time: datetime, 
                        end_time: datetime, attendee_email: str = None, 
                        calendar_id: str = 'primary') -> Dict:
        """Book an appointment"""
        try:
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            if attendee_email:
                event['attendees'] = [{'email': attendee_email}]
            
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            
            return {
                'success': True,
                'event_id': created_event.get('id'),
                'event_link': created_event.get('htmlLink'),
                'message': f'Appointment booked successfully for {start_time.strftime("%B %d, %Y at %I:%M %p")}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to book appointment'
            }