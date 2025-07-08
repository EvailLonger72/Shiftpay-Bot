from datetime import datetime, time, timedelta
from typing import Optional

class TimeUtils:
    def parse_time(self, time_str: str) -> Optional[datetime]:
        """Parse time string to datetime object."""
        try:
            # Remove any extra whitespace
            time_str = time_str.strip()
            
            # Parse HH:MM format
            if ':' in time_str:
                hour, minute = map(int, time_str.split(':'))
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    # Use today's date as base
                    today = datetime.now().date()
                    return datetime.combine(today, time(hour, minute))
            
            return None
        except (ValueError, TypeError):
            return None
    
    def calculate_total_minutes(self, start_time: datetime, end_time: datetime) -> int:
        """Calculate total minutes between start and end time."""
        # Handle cases where end time is next day
        if end_time < start_time:
            end_time = end_time + timedelta(days=1)
        
        diff = end_time - start_time
        return int(diff.total_seconds() / 60)
    
    def calculate_overlap(self, work_start: datetime, work_end: datetime,
                         break_start: datetime, break_end: datetime) -> int:
        """Calculate overlap between work time and break time in minutes."""
        # Handle cases where times cross midnight
        if work_end < work_start:
            work_end = work_end + timedelta(days=1)
        
        if break_end < break_start:
            break_end = break_end + timedelta(days=1)
        
        # Find overlap
        overlap_start = max(work_start, break_start)
        overlap_end = min(work_end, break_end)
        
        if overlap_start < overlap_end:
            diff = overlap_end - overlap_start
            return int(diff.total_seconds() / 60)
        
        return 0
    
    def format_duration(self, minutes: int) -> str:
        """Format duration in minutes to hours and minutes."""
        hours = minutes // 60
        mins = minutes % 60
        
        if hours > 0 and mins > 0:
            return f"{hours}နာရီ {mins}မိနစ်"
        elif hours > 0:
            return f"{hours}နာရီ"
        else:
            return f"{mins}မိနစ်"
    
    def format_time_range(self, start_time: datetime, end_time: datetime) -> str:
        """Format time range for display."""
        start_str = start_time.strftime("%H:%M")
        end_str = end_time.strftime("%H:%M")
        return f"{start_str} → {end_str}"
    
    def minutes_to_decimal_hours(self, minutes: int) -> float:
        """Convert minutes to decimal hours."""
        return round(minutes / 60, 2)
