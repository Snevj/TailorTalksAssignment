import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain.schema import SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
from dateutil import parser
import pytz

from calendar_service import GoogleCalendarService

class CalendarBookingAgent:
    def __init__(self, credentials_path: str, gemini_api_key: str):
        self.calendar_service = GoogleCalendarService(credentials_path)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=gemini_api_key,
            temperature=0.7
        )
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=10
        )
        self.agent_executor = self._create_agent()
    def _safe_parse_input(self, x: str) -> dict:
        """Safely parse input string to dictionary"""
        import json
        if x.startswith('{'):
            try:
                return json.loads(x)
            except json.JSONDecodeError:
                return {'date_str': x}
        return {'date_str': x}
    
    def _parse_datetime(self, date_str: str, time_str: str = None) -> datetime:
        """Parse date and time strings into datetime object"""
        try:
            if time_str:
                datetime_str = f"{date_str} {time_str}"
            else:
                datetime_str = date_str
            
            parsed_dt = parser.parse(datetime_str)
            return parsed_dt
        except Exception as e:
            print(f"Error parsing datetime: {e}")
            return None
    
    def check_availability_tool(self, date_str: str, time_str: str = None, duration: int = 60) -> str:
        """Tool to check availability for a specific date and time"""
        try:
            target_date = self._parse_datetime(date_str, time_str)
            if not target_date:
                return "I couldn't understand the date format. Please provide date in a clear format like 'December 15, 2024' or '2024-12-15'."
            
            if time_str:
                # Check specific time slot
                end_time = target_date + timedelta(minutes=duration)
                is_available = self.calendar_service.check_availability(target_date, end_time)
                
                if is_available:
                    return f"Good news! The time slot on {target_date.strftime('%B %d, %Y')} at {target_date.strftime('%I:%M %p')} is available."
                else:
                    return f"Unfortunately, the time slot on {target_date.strftime('%B %d, %Y')} at {target_date.strftime('%I:%M %p')} is not available. Let me suggest some alternatives."
            else:
                # Get available slots for the entire day
                available_slots = self.calendar_service.get_available_slots(target_date, duration)
                
                if available_slots:
                    slot_times = [slot['formatted_time'] for slot in available_slots[:5]]  # Show first 5 slots
                    return f"Here are available time slots for {target_date.strftime('%B %d, %Y')}: {', '.join(slot_times)}"
                else:
                    return f"No available slots found for {target_date.strftime('%B %d, %Y')}. Would you like to try a different date?"
                    
        except Exception as e:
            return f"I encountered an error while checking availability: {str(e)}"
    
    def book_appointment_tool(self, title: str, date_str: str, time_str: str, 
                            duration: int = 60, description: str = "", 
                            attendee_email: str = None) -> str:
        """Tool to book an appointment"""
        try:
            start_time = self._parse_datetime(date_str, time_str)
            if not start_time:
                return "I couldn't understand the date/time format. Please provide clear date and time."
            
            end_time = start_time + timedelta(minutes=duration)
            
            # Check availability first
            if not self.calendar_service.check_availability(start_time, end_time):
                return f"Sorry, the time slot on {start_time.strftime('%B %d, %Y')} at {start_time.strftime('%I:%M %p')} is not available. Please choose a different time."
            
            # Book the appointment
            result = self.calendar_service.book_appointment(
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                attendee_email=attendee_email
            )
            
            if result['success']:
                return f"Perfect! I've successfully booked your appointment '{title}' for {start_time.strftime('%B %d, %Y')} at {start_time.strftime('%I:%M %p')}. Duration: {duration} minutes."
            else:
                return f"I couldn't book the appointment: {result['message']}"
                
        except Exception as e:
            return f"I encountered an error while booking: {str(e)}"
    
    def get_available_slots_tool(self, date_str: str, duration: int = 60) -> str:
        """Tool to get available slots for a specific date"""
        try:
            target_date = self._parse_datetime(date_str)
            if not target_date:
                return "Please provide a valid date format."
            
            available_slots = self.calendar_service.get_available_slots(target_date, duration)
            
            if available_slots:
                slot_list = []
                for i, slot in enumerate(available_slots[:8], 1):  # Show up to 8 slots
                    slot_list.append(f"{i}. {slot['formatted_time']}")
                
                return f"Available time slots for {target_date.strftime('%B %d, %Y')}:\n" + "\n".join(slot_list)
            else:
                return f"No available slots found for {target_date.strftime('%B %d, %Y')}."
                
        except Exception as e:
            return f"Error getting available slots: {str(e)}"
    
    def _create_agent(self):
        """Create the LangChain agent with tools"""
        tools = [
            Tool(
                name="check_availability",
                func=lambda x: self.check_availability_tool(**self._safe_parse_input(x)),
                description="Check availability for a specific date and optionally time. Input should be a date string or JSON with date_str, time_str, and duration."
            ),
            Tool(
                name="book_appointment",
                func=lambda x: self.book_appointment_tool(**self._safe_parse_input(x)),
                description="Book an appointment. Input should be JSON with title, date_str, time_str, duration (optional), description (optional), and attendee_email (optional)."
            ),
            Tool(
                name="get_available_slots",
                func=lambda x: self.get_available_slots_tool(**self._safe_parse_input(x)),
                description="Get all available time slots for a specific date. Input should be a date string or JSON with date_str and duration."
            )
        ]
        
        system_message = """You are TailorTalk, a friendly and efficient calendar booking assistant. Your job is to help users book appointments seamlessly through natural conversation.

Key capabilities:
- Check calendar availability for specific dates and times
- Suggest available time slots
- Book appointments with all necessary details
- Handle natural language date/time requests
- Provide a conversational, helpful experience

Guidelines:
1. Always be conversational and friendly
2. Ask for clarification when needed (date, time, appointment title, duration)
3. Confirm details before booking
4. Use the tools to check availability and book appointments
5. Handle date/time parsing intelligently
6. Suggest alternatives if requested times aren't available

When using tools, format the input as JSON strings with appropriate parameters.

Example tool calls:
- check_availability: '{"date_str": "December 15, 2024", "time_str": "2:00 PM", "duration": 60}'
- book_appointment: '{"title": "Team Meeting", "date_str": "December 15, 2024", "time_str": "2:00 PM", "duration": 60, "description": "Weekly team sync"}'
- get_available_slots: '{"date_str": "December 15, 2024", "duration": 60}'

Always confirm booking details with the user before finalizing appointments."""

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def chat(self, message: str) -> str:
        """Process user message and return response"""
        try:
            response = self.agent_executor.invoke({"input": message})
            return response["output"]
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Could you please rephrase your request?"