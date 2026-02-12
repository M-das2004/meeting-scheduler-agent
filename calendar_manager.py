import json
import zlib
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uuid

class CalendarManager:
    def __init__(self):
        self.meetings = []
    
    def add_meeting(self, title: str, start_time: datetime, end_time: datetime, 
                    attendees: str, description: str = "", duration: int = 30) -> str:
        """Add a new meeting to the calendar"""
        meeting_id = str(uuid.uuid4())[:8]
        
        meeting = {
            'id': meeting_id,
            'title': title,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'attendees': attendees,
            'description': description,
            'duration': duration,
            'created_at': datetime.now().isoformat()
        }
        
        self.meetings.append(meeting)
        return meeting_id
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting by ID"""
        original_length = len(self.meetings)
        self.meetings = [m for m in self.meetings if m['id'] != meeting_id]
        return len(self.meetings) < original_length
    
    def get_all_meetings(self) -> List[Dict]:
        """Get all meetings"""
        return self.meetings
    
    def get_meetings_in_range(self, start_date, end_date) -> List[Dict]:
        """Get meetings within a date range"""
        result = []
        
        # Convert date objects to datetime if needed
        if not isinstance(start_date, datetime):
            start_date = datetime.combine(start_date, datetime.min.time())
        if not isinstance(end_date, datetime):
            end_date = datetime.combine(end_date, datetime.max.time())
        
        for meeting in self.meetings:
            meeting_start = datetime.fromisoformat(meeting['start_time'])
            if start_date <= meeting_start <= end_date:
                result.append(meeting)
        return result
    
    def check_conflicts(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Check for scheduling conflicts"""
        conflicts = []
        
        for meeting in self.meetings:
            meeting_start = datetime.fromisoformat(meeting['start_time'])
            meeting_end = datetime.fromisoformat(meeting['end_time'])
            
            # Check if times overlap
            if (start_time < meeting_end and end_time > meeting_start):
                conflicts.append(meeting)
        
        return conflicts
    
    def get_availability(self, date: datetime, work_start: int = 9, work_end: int = 17) -> List[Dict]:
        """Get available time slots for a given day"""
        day_start = datetime.combine(date.date(), datetime.min.time()).replace(hour=work_start)
        day_end = datetime.combine(date.date(), datetime.min.time()).replace(hour=work_end)
        
        # Get meetings for this day
        day_meetings = []
        for meeting in self.meetings:
            meeting_start = datetime.fromisoformat(meeting['start_time'])
            if meeting_start.date() == date.date():
                day_meetings.append({
                    'start': meeting_start,
                    'end': datetime.fromisoformat(meeting['end_time'])
                })
        
        # Sort by start time
        day_meetings.sort(key=lambda x: x['start'])
        
        # Find available slots
        available_slots = []
        current_time = day_start
        
        for meeting in day_meetings:
            if current_time < meeting['start']:
                available_slots.append({
                    'start': current_time,
                    'end': meeting['start']
                })
            current_time = max(current_time, meeting['end'])
        
        # Add remaining time at end of day
        if current_time < day_end:
            available_slots.append({
                'start': current_time,
                'end': day_end
            })
        
        return available_slots
    
    def compress_calendar_data(self) -> str:
        """Compress calendar data for efficient storage/transmission"""
        json_str = json.dumps(self.meetings)
        compressed = zlib.compress(json_str.encode('utf-8'))
        return base64.b64encode(compressed).decode('utf-8')
    
    def decompress_calendar_data(self, compressed_str: str) -> List[Dict]:
        """Decompress calendar data"""
        compressed = base64.b64decode(compressed_str.encode('utf-8'))
        json_str = zlib.decompress(compressed).decode('utf-8')
        return json.loads(json_str)
    
    def get_calendar_summary(self, start_date: datetime, end_date: datetime) -> str:
        """Create a concise summary of calendar for AI processing"""
        meetings = self.get_meetings_in_range(start_date, end_date)
        
        if not meetings:
            return "No meetings scheduled in this period."
        
        summary = f"Calendar Summary ({start_date.date()} to {end_date.date()}):\n"
        summary += f"Total Meetings: {len(meetings)}\n\n"
        
        for meeting in sorted(meetings, key=lambda x: x['start_time']):
            start = datetime.fromisoformat(meeting['start_time'])
            summary += f"- {meeting['title']}: {start.strftime('%b %d, %I:%M %p')} ({meeting['duration']}min)\n"
        
        return summary
    
    def get_busy_hours(self) -> Dict[int, int]:
        """Get meeting count by hour of day"""
        hour_counts = {}
        
        for meeting in self.meetings:
            start = datetime.fromisoformat(meeting['start_time'])
            hour = start.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        return hour_counts