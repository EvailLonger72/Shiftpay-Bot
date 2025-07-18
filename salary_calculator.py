from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from shift_detector import ShiftDetector
from time_utils import TimeUtils

class SalaryCalculator:
    def __init__(self):
        self.shift_detector = ShiftDetector()
        self.time_utils = TimeUtils()
        
        # Salary rates (in yen per hour)
        self.BASE_RATE = 2100
        self.NIGHT_OT_RATE = 2625
        self.REGULAR_HOURS_LIMIT = 7 * 60 + 35  # 7h35m in minutes
        self.NIGHT_START_HOUR = 22  # 22:00
    
    def calculate_salary(self, start_time_str: str, end_time_str: str) -> Dict:
        """Calculate salary based on start and end times."""
        try:
            # Parse time strings
            start_time = self.time_utils.parse_time(start_time_str)
            end_time = self.time_utils.parse_time(end_time_str)
            
            if not start_time or not end_time:
                return {'error': 'အချိန်ပုံစံမှားနေသည်။ ဥပမာ: 08:30 ~ 17:30'}
            
            # Detect shift type
            shift_type = self.shift_detector.detect_shift(start_time, end_time)
            
            if not shift_type:
                return {'error': 'Shift အမျိုးအစားမသိရှိပါ။'}
            
            # Get shift configuration
            shift_config = self.shift_detector.get_shift_config(shift_type)
            
            # Calculate total work minutes
            total_minutes = self.time_utils.calculate_total_minutes(start_time, end_time)
            
            # Calculate break deductions
            break_minutes, break_details = self.calculate_break_deductions(
                start_time, end_time, shift_config['breaks']
            )
            
            # Calculate paid work time
            paid_minutes = total_minutes - break_minutes
            
            # Split into regular, overtime, and night overtime
            regular_minutes, ot_minutes, night_ot_minutes = self.split_work_hours(
                start_time, end_time, paid_minutes
            )
            
            # Calculate salary with proper night shift handling
            regular_salary = (regular_minutes / 60) * self.BASE_RATE
            
            # Night shift: 22:00 နာရီကျော်တာနဲ့ AUTO 2625¥, နောက်နေ့ရောက်လဲ 2625¥
            if shift_type == 'C342' or end_time.date() > start_time.date():
                # Night shift or work crosses midnight - all OT at 2625¥ rate
                ot_salary = (ot_minutes / 60) * self.NIGHT_OT_RATE
                night_ot_salary = (night_ot_minutes / 60) * self.NIGHT_OT_RATE
            else:
                # Day shift - regular OT at 2100¥, night OT at 2625¥
                ot_salary = (ot_minutes / 60) * self.BASE_RATE
                night_ot_salary = (night_ot_minutes / 60) * self.NIGHT_OT_RATE
            
            total_salary = regular_salary + ot_salary + night_ot_salary
            
            return {
                'error': None,
                'shift_type': shift_type,
                'start_time': start_time,
                'end_time': end_time,
                'total_minutes': total_minutes,
                'break_minutes': break_minutes,
                'break_details': break_details,
                'paid_minutes': paid_minutes,
                'regular_minutes': regular_minutes,
                'ot_minutes': ot_minutes,
                'night_ot_minutes': night_ot_minutes,
                'regular_salary': regular_salary,
                'ot_salary': ot_salary,
                'night_ot_salary': night_ot_salary,
                'total_salary': total_salary
            }
            
        except Exception as e:
            return {'error': f'တွက်ချက်မှုအမှား: {str(e)}'}
    
    def calculate_break_deductions(self, start_time: datetime, end_time: datetime, 
                                 breaks: List[Tuple[str, str]]) -> Tuple[int, List[Dict]]:
        """Calculate break time deductions based on overlap with work time."""
        total_break_minutes = 0
        break_details = []
        
        for break_start_str, break_end_str in breaks:
            break_start = self.time_utils.parse_time(break_start_str)
            break_end = self.time_utils.parse_time(break_end_str)
            
            if not break_start or not break_end:
                continue
            
            # Handle breaks that cross midnight
            if break_end < break_start:
                break_end = break_end + timedelta(days=1)
            
            # Check if work time overlaps with break time
            overlap_minutes = self.time_utils.calculate_overlap(
                start_time, end_time, break_start, break_end
            )
            
            if overlap_minutes > 0:
                total_break_minutes += overlap_minutes
                break_details.append({
                    'start': break_start_str,
                    'end': break_end_str,
                    'minutes': overlap_minutes
                })
        
        return total_break_minutes, break_details
    
    def split_work_hours(self, start_time: datetime, end_time: datetime, 
                        paid_minutes: int) -> Tuple[int, int, int]:
        """Split work hours into regular, overtime, and night overtime."""
        # Regular hours up to 7h35m
        regular_minutes = min(paid_minutes, self.REGULAR_HOURS_LIMIT)
        total_overtime_minutes = max(0, paid_minutes - self.REGULAR_HOURS_LIMIT)
        
        # Check if work crosses midnight (next day) or is night shift
        crosses_midnight = end_time.date() > start_time.date()
        is_night_shift = start_time.hour >= 16  # Night shift typically starts at 16:00 or later
        
        # Night shift logic: 22:00 နာရီကျော်တာနဲ့ AUTO 2625¥, နောက်နေ့ရောက်လဲ 2625¥
        if is_night_shift or crosses_midnight:
            # Night shift: All OT at 2625¥ rate
            if total_overtime_minutes > 0:
                night_ot_minutes = total_overtime_minutes
                regular_ot_minutes = 0
            else:
                night_ot_minutes = 0
                regular_ot_minutes = 0
        else:
            # Day shift: Check if OT occurs after 22:00
            night_ot_minutes = self.calculate_night_overtime(start_time, end_time, paid_minutes)
            regular_ot_minutes = total_overtime_minutes - night_ot_minutes
        
        return regular_minutes, regular_ot_minutes, night_ot_minutes
    
    def calculate_night_overtime(self, start_time: datetime, end_time: datetime, 
                               paid_minutes: int) -> int:
        """Calculate night overtime minutes (work after 22:00)."""
        # Create 22:00 time for comparison
        night_start = start_time.replace(hour=self.NIGHT_START_HOUR, minute=0, second=0, microsecond=0)
        
        # Handle next day end time
        if end_time.date() > start_time.date():
            # Work crosses midnight - adjust night_start for next day calculation
            pass
        
        # If work ends before 22:00, no night OT
        if end_time <= night_start and end_time.date() == start_time.date():
            return 0
        
        # If work starts after 22:00, all overtime is night OT
        if start_time >= night_start:
            return max(0, paid_minutes - self.REGULAR_HOURS_LIMIT)
        
        # Calculate work time after 22:00
        if end_time.date() > start_time.date():
            # Work crosses midnight - all work after 22:00 is night OT
            night_work_start = max(start_time, night_start)
            night_work_minutes = self.time_utils.calculate_total_minutes(night_work_start, end_time)
        else:
            # Same day work - calculate time after 22:00
            night_work_minutes = self.time_utils.calculate_total_minutes(night_start, end_time)
        
        # Night OT is the portion of overtime that happens after 22:00
        total_ot_minutes = max(0, paid_minutes - self.REGULAR_HOURS_LIMIT)
        
        return min(night_work_minutes, total_ot_minutes)
