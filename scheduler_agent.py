from datetime import datetime, timedelta
from typing import List, Dict
import random

class MeetingSchedulerAgent:
    def __init__(self, preferences: Dict):
        self.preferences = preferences
    
    def find_optimal_slots(self, start_date, end_date, 
                          duration: int, existing_meetings: List[Dict],
                          preferences: Dict) -> List[Dict]:
        """Find optimal meeting slots using intelligent scheduling"""
        
        optimal_slots = []
        
        # Convert date objects to datetime if needed
        if not isinstance(start_date, datetime):
            current_date = datetime.combine(start_date, datetime.min.time())
        else:
            current_date = start_date
            
        if not isinstance(end_date, datetime):
            end_date_dt = datetime.combine(end_date, datetime.max.time())
        else:
            end_date_dt = end_date
        
        # Convert existing meetings to datetime objects for easier comparison
        busy_times = []
        for meeting in existing_meetings:
            busy_times.append({
                'start': datetime.fromisoformat(meeting['start_time']),
                'end': datetime.fromisoformat(meeting['end_time'])
            })
        
        # Iterate through each day in the range
        while current_date <= end_date_dt:
            # Skip weekends
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                current_date += timedelta(days=1)
                continue
            
            # Get available slots for this day
            day_slots = self._find_day_slots(
                current_date,
                duration,
                busy_times,
                preferences
            )
            
            optimal_slots.extend(day_slots)
            current_date += timedelta(days=1)
        
        # Sort by score
        optimal_slots.sort(key=lambda x: x['score'], reverse=True)
        
        return optimal_slots
    
    def _find_day_slots(self, date: datetime, duration: int, 
                       busy_times: List[Dict], preferences: Dict) -> List[Dict]:
        """Find available slots for a specific day"""
        
        work_start = preferences.get('work_hours_start', 9)
        work_end = preferences.get('work_hours_end', 17)
        buffer_time = preferences.get('buffer_time', 15)
        
        slots = []
        
        # Start from work start time
        current_time = datetime.combine(date.date(), datetime.min.time()).replace(hour=work_start)
        day_end = datetime.combine(date.date(), datetime.min.time()).replace(hour=work_end)
        
        while current_time + timedelta(minutes=duration) <= day_end:
            slot_end = current_time + timedelta(minutes=duration)
            
            # Check if this slot conflicts with existing meetings
            has_conflict = False
            for busy in busy_times:
                if (current_time < busy['end'] and slot_end > busy['start']):
                    has_conflict = True
                    # Jump to end of conflicting meeting plus buffer
                    current_time = busy['end'] + timedelta(minutes=buffer_time)
                    break
            
            if not has_conflict:
                # Score this slot
                score = self._score_slot(current_time, duration, preferences)
                
                slots.append({
                    'start': current_time,
                    'end': slot_end,
                    'score': score,
                    'reason': self._get_score_reason(current_time, score)
                })
                
                # Move to next potential slot
                current_time += timedelta(minutes=30)  # Check every 30 minutes
        
        return slots
    
    def _score_slot(self, time: datetime, duration: int, preferences: Dict) -> int:
        """Score a time slot based on preferences (0-100)"""
        score = 50  # Base score
        
        hour = time.hour
        
        # Morning preference (9 AM - 11 AM gets bonus)
        if 9 <= hour < 11:
            score += 20
        
        # Early afternoon preference (2 PM - 4 PM gets bonus)
        elif 14 <= hour < 16:
            score += 15
        
        # Late afternoon penalty (after 4 PM)
        elif hour >= 16:
            score -= 10
        
        # Very early or late penalty
        if hour < 9 or hour >= 17:
            score -= 20
        
        # Lunch time penalty (12 PM - 1 PM)
        if 12 <= hour < 13:
            score -= 15
        
        # Start of week bonus (Tuesday-Thursday)
        if 1 <= time.weekday() <= 3:
            score += 10
        
        # Monday penalty (people need to catch up)
        if time.weekday() == 0:
            score -= 5
        
        # Friday afternoon penalty
        if time.weekday() == 4 and hour >= 15:
            score -= 15
        
        # Duration factor (longer meetings better in morning)
        if duration >= 60 and hour < 12:
            score += 10
        
        # Ensure score is in valid range
        return max(0, min(100, score))
    
    def _get_score_reason(self, time: datetime, score: int) -> str:
        """Generate human-readable reason for score"""
        hour = time.hour
        day = time.strftime('%A')
        
        reasons = []
        
        if score >= 80:
            reasons.append("Optimal time slot")
        elif score >= 60:
            reasons.append("Good time slot")
        else:
            reasons.append("Available slot")
        
        if 9 <= hour < 11:
            reasons.append("morning focus time")
        elif 14 <= hour < 16:
            reasons.append("afternoon productivity window")
        elif hour >= 16:
            reasons.append("late afternoon - may be less ideal")
        
        if 12 <= hour < 13:
            reasons.append("during typical lunch hour")
        
        if 1 <= time.weekday() <= 3:
            reasons.append(f"mid-week ({day})")
        elif time.weekday() == 0:
            reasons.append("Monday - busy catch-up day")
        elif time.weekday() == 4:
            reasons.append("Friday - end of week")
        
        return ", ".join(reasons)
    
    def suggest_reschedule(self, meeting_id: str, current_time: datetime, 
                          available_slots: List[Dict]) -> Dict:
        """Suggest better time to reschedule a meeting"""
        
        # Filter slots that are at least 1 hour away from current time
        future_slots = [
            slot for slot in available_slots 
            if slot['start'] > current_time + timedelta(hours=1)
        ]
        
        if not future_slots:
            return None
        
        # Return highest scored slot
        best_slot = max(future_slots, key=lambda x: x['score'])
        
        return {
            'suggested_time': best_slot['start'],
            'reason': f"Better slot found: {best_slot['reason']}",
            'score_improvement': best_slot['score']
        }
    
    def check_meeting_load(self, date: datetime, existing_meetings: List[Dict]) -> Dict:
        """Check if a day is overloaded with meetings"""
        
        day_meetings = [
            m for m in existing_meetings
            if datetime.fromisoformat(m['start_time']).date() == date.date()
        ]
        
        total_duration = sum(m['duration'] for m in day_meetings)
        meeting_count = len(day_meetings)
        
        max_meetings = self.preferences.get('max_meetings_per_day', 5)
        
        return {
            'date': date.date(),
            'meeting_count': meeting_count,
            'total_duration_minutes': total_duration,
            'is_overloaded': meeting_count >= max_meetings,
            'utilization_percentage': (total_duration / 480) * 100  # 8 hour workday
        }