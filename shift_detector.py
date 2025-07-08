from datetime import datetime, time
from typing import Optional, Dict, List, Tuple

class ShiftDetector:
    def __init__(self):
        self.shifts = {
            'C341': {
                'name': 'Day Shift',
                'start': time(8, 30),
                'end': time(17, 30),
                'breaks': [
                    ('08:30', '08:40'),  # 10 min
                    ('10:40', '11:25'),  # 45 min
                    ('13:05', '13:15'),  # 10 min
                    ('14:35', '14:45'),  # 10 min
                    ('16:10', '16:20'),  # 10 min
                    ('17:20', '17:35'),  # 15 min
                ]
            },
            'C342': {
                'name': 'Night Shift',
                'start': time(16, 45),
                'end': time(1, 25),  # Next day
                'breaks': [
                    ('18:45', '18:55'),  # 10 min
                    ('20:55', '21:40'),  # 45 min
                    ('23:10', '23:20'),  # 10 min
                    ('00:50', '01:00'),  # 10 min
                    ('02:25', '02:35'),  # 10 min
                    ('03:35', '03:50'),  # 15 min
                ]
            }
        }
    
    def detect_shift(self, start_time: datetime, end_time: datetime) -> Optional[str]:
        """Detect shift type based on start and end times."""
        start_time_only = start_time.time()
        end_time_only = end_time.time()
        
        # Check for Day Shift (C341)
        if self._is_day_shift(start_time_only, end_time_only):
            return 'C341'
        
        # Check for Night Shift (C342)
        if self._is_night_shift(start_time_only, end_time_only):
            return 'C342'
        
        # If exact match not found, determine based on start time
        if start_time_only >= time(6, 0) and start_time_only <= time(12, 0):
            return 'C341'  # Morning start likely day shift
        elif start_time_only >= time(16, 0) and start_time_only <= time(23, 59):
            return 'C342'  # Evening start likely night shift
        
        return None
    
    def _is_day_shift(self, start_time: time, end_time: time) -> bool:
        """Check if times match day shift pattern."""
        day_start = self.shifts['C341']['start']
        day_end = self.shifts['C341']['end']
        
        # Allow some flexibility (±30 minutes)
        start_diff = abs(self._time_to_minutes(start_time) - self._time_to_minutes(day_start))
        end_diff = abs(self._time_to_minutes(end_time) - self._time_to_minutes(day_end))
        
        return start_diff <= 30 and end_diff <= 30
    
    def _is_night_shift(self, start_time: time, end_time: time) -> bool:
        """Check if times match night shift pattern."""
        night_start = self.shifts['C342']['start']
        night_end = self.shifts['C342']['end']
        
        # Allow some flexibility (±30 minutes)
        start_diff = abs(self._time_to_minutes(start_time) - self._time_to_minutes(night_start))
        
        # For night shift end time, handle next day
        end_minutes = self._time_to_minutes(end_time)
        if end_time < time(12, 0):  # Likely next day
            end_minutes += 24 * 60
        
        night_end_minutes = self._time_to_minutes(night_end) + 24 * 60
        end_diff = abs(end_minutes - night_end_minutes)
        
        return start_diff <= 30 and end_diff <= 30
    
    def _time_to_minutes(self, t: time) -> int:
        """Convert time to minutes since midnight."""
        return t.hour * 60 + t.minute
    
    def get_shift_config(self, shift_type: str) -> Dict:
        """Get shift configuration."""
        return self.shifts.get(shift_type, {})
    
    def get_shift_name(self, shift_type: str) -> str:
        """Get shift name in Burmese."""
        names = {
            'C341': 'နေ့ပိုင်းအလုပ်',
            'C342': 'ညပိုင်းအလုပ်'
        }
        return names.get(shift_type, 'အမျိုးအစားမသိ')
