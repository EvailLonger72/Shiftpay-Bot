from datetime import datetime, timedelta
from typing import Dict, List
from time_utils import TimeUtils
from shift_detector import ShiftDetector

class BurmeseFormatter:
    def __init__(self):
        self.time_utils = TimeUtils()
        self.shift_detector = ShiftDetector()
    
    def format_salary_response(self, result: Dict) -> str:
        """Format salary calculation result into Burmese Telegram message."""
        if result.get('error'):
            return f"❌ **အမှားရှိသည်**\n\n{result['error']}"
        
        # Get current date
        today = datetime.now().strftime("%Y/%m/%d")
        
        # Format time range
        time_range = self.time_utils.format_time_range(result['start_time'], result['end_time'])
        
        # Format durations
        total_duration = self.time_utils.format_duration(result['total_minutes'])
        break_duration = self.time_utils.format_duration(result['break_minutes'])
        paid_duration = self.time_utils.format_duration(result['paid_minutes'])
        
        # Get shift name
        shift_name = self.shift_detector.get_shift_name(result['shift_type'])
        
        # Format salary breakdown
        salary_breakdown = self._format_salary_breakdown(result)
        
        # Generate visual diagram
        diagram = self._generate_diagram(result)
        
        # Generate visual timeline
        timeline = self._generate_timeline(result)
        
        # Construct the full response as a visual timeline
        response = f"""✅ **{time_range}** – {total_duration}
🟦 **Break {result['break_minutes']} မိနစ် နုတ်ပြီး** – {paid_duration}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{salary_breakdown}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 **စုစုပေါင်း = ¥{result['total_salary']:,.0f}**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{timeline}"""
        
        return response
    
    def _format_salary_breakdown(self, result: Dict) -> str:
        """Format the salary breakdown section."""
        breakdown = "📊 **လစာ Breakdown**\n\n"
        
        # Regular hours
        if result['regular_minutes'] > 0:
            regular_hours = self.time_utils.minutes_to_decimal_hours(result['regular_minutes'])
            breakdown += f"🟢 **ပုံမှန်နာရီ ({regular_hours} နာရီ)**\n"
            breakdown += f"→ ¥2,100 × {regular_hours} = ¥{result['regular_salary']:,.0f}\n"
        
        # Overtime
        if result['ot_minutes'] > 0:
            ot_hours = self.time_utils.minutes_to_decimal_hours(result['ot_minutes'])
            breakdown += f"🔵 **OT ({ot_hours} နာရီ)**\n"
            breakdown += f"→ ¥2,100 × {ot_hours} = ¥{result['ot_salary']:,.0f}\n"
        else:
            breakdown += "🔵 **OT = 0**\n"
        
        # Night overtime
        if result['night_ot_minutes'] > 0:
            night_ot_hours = self.time_utils.minutes_to_decimal_hours(result['night_ot_minutes'])
            breakdown += f"🌙 **Night OT ({night_ot_hours} နာရီ)**\n"
            breakdown += f"→ ¥2,625 × {night_ot_hours} = ¥{result['night_ot_salary']:,.0f}\n"
        else:
            breakdown += "🌙 **Night OT = 0**\n"
        
        return breakdown
    
    def _generate_timeline(self, result: Dict) -> str:
        """Generate a visual timeline similar to the provided image."""
        timeline_parts = []
        
        # Create timeline based on breaks
        current_time = result['start_time']
        
        # Process breaks that overlap with work time
        for break_detail in result['break_details']:
            break_start = self.time_utils.parse_time(break_detail['start'])
            break_end = self.time_utils.parse_time(break_detail['end'])
            
            if break_start and break_end:
                # Handle breaks that cross midnight
                if break_end < break_start:
                    break_end = break_end + timedelta(days=1)
                
                # Add work period before break
                if break_start > current_time:
                    timeline_parts.append(f"{current_time.strftime('%H:%M')} 🟩━━━━━━━━{break_start.strftime('%H:%M')} 🔵")
                    current_time = break_start
                
                # Add break period
                timeline_parts.append(f"{break_start.strftime('%H:%M')} 🔵━━━━━━━━{break_end.strftime('%H:%M')} 🟩")
                current_time = break_end
        
        # Add final work period
        if current_time < result['end_time']:
            timeline_parts.append(f"{current_time.strftime('%H:%M')} 🟩━━━━━━━━{result['end_time'].strftime('%H:%M')}")
        
        # If no breaks processed, show simple work period
        if not timeline_parts:
            timeline_parts.append(f"{result['start_time'].strftime('%H:%M')} 🟩━━━━━━━━{result['end_time'].strftime('%H:%M')}")
        
        # Join timeline parts and add legend
        timeline = "\n".join(timeline_parts)
        timeline += "\n\n🟩 = အလုပ်ချိန်　🔵 = Break ချိန်"
        
        return timeline
    
    def _generate_diagram(self, result: Dict) -> str:
        """Generate a visual diagram of work periods and breaks."""
        diagram = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        diagram += "📊 **Diagram**\n"
        diagram += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        # Get shift configuration
        shift_config = self.shift_detector.get_shift_config(result['shift_type'])
        breaks = shift_config.get('breaks', [])
        
        # Create timeline
        timeline_parts = []
        current_time = result['start_time']
        
        # Add start time
        timeline_parts.append(f"[{current_time.strftime('%H:%M')}]")
        
        # Process breaks that overlap with work time
        for break_detail in result['break_details']:
            break_start = self.time_utils.parse_time(break_detail['start'])
            break_end = self.time_utils.parse_time(break_detail['end'])
            
            if break_start and break_end:
                # Handle breaks that cross midnight
                if break_end < break_start:
                    break_end = break_end + timedelta(days=1)
                
                # Add work period before break
                if break_start > current_time:
                    timeline_parts.append(" 🟩───")
                    timeline_parts.append(f"[{break_start.strftime('%H:%M')}]")
                
                # Add break period
                timeline_parts.append(" 🔵───")
                timeline_parts.append(f"[{break_end.strftime('%H:%M')}]")
                
                current_time = break_end
        
        # Add final work period
        if current_time < result['end_time']:
            timeline_parts.append(" 🟩───")
            timeline_parts.append(f"[{result['end_time'].strftime('%H:%M')}]")
        
        # Format timeline into lines (max ~50 chars per line for Telegram)
        lines = []
        current_line = ""
        
        for part in timeline_parts:
            if len(current_line + part) > 50:
                lines.append(current_line)
                current_line = part
            else:
                current_line += part
        
        if current_line:
            lines.append(current_line)
        
        # Add lines to diagram
        for line in lines:
            diagram += line + "\n"
        
        # Add legend
        diagram += "\n🟩 = အလုပ်ချိန်　🔵 = Break ချိန်"
        
        return diagram
    
    def format_break_details(self, break_details: List[Dict]) -> str:
        """Format break details for display."""
        if not break_details:
            return "Break မရှိပါ"
        
        details = []
        for break_info in break_details:
            duration = self.time_utils.format_duration(break_info['minutes'])
            details.append(f"• {break_info['start']}~{break_info['end']} ({duration})")
        
        return "\n".join(details)
    
    def format_error_message(self, error: str) -> str:
        """Format error message in Burmese."""
        return f"❌ **အမှားရှိသည်**\n\n{error}\n\n📝 **မှန်ကန်သောပုံစံ:** 08:30 ~ 17:30"
from datetime import datetime
from typing import Dict

class BurmeseFormatter:
    """Format calculation results into Burmese Telegram messages."""
    
    def format_salary_response(self, result: Dict) -> str:
        """Format salary calculation result into Burmese message."""
        if result.get('error'):
            return f"❌ **အမှားရှိသည်**\n\n{result['error']}"
        
        # Basic information
        shift_name = "နေ့ပိုင်း" if result['shift_type'] == 'C341' else "ညပိုင်း"
        start_time = result['start_time'].strftime('%H:%M')
        end_time = result['end_time'].strftime('%H:%M')
        
        # Time calculations
        total_hours = self._minutes_to_hours(result['total_minutes'])
        break_hours = self._minutes_to_hours(result['break_minutes'])
        paid_hours = self._minutes_to_hours(result['paid_minutes'])
        regular_hours = self._minutes_to_hours(result['regular_minutes'])
        ot_hours = self._minutes_to_hours(result['ot_minutes'])
        night_ot_hours = self._minutes_to_hours(result['night_ot_minutes'])
        
        # Format salary amounts
        total_salary = result['total_salary']
        regular_salary = result['regular_salary']
        ot_salary = result['ot_salary']
        night_ot_salary = result['night_ot_salary']
        
        response = f"""💰 **လစာတွက်ချက်မှုရလဒ်**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🕒 **အချိန်:** {start_time} ~ {end_time}
🏭 **Shift:** {result['shift_type']} ({shift_name})

⏰ **အချိန်ခွဲခြမ်းမှု:**
   📊 စုစုပေါင်း: {total_hours}
   ☕ Break: {break_hours}
   💼 လုပ်ငန်း: {paid_hours}

💼 **လုပ်ငန်းအချိန်ပိုင်းခြား:**
   🟢 ပုံမှန်: {regular_hours}
   🔵 OT: {ot_hours}
   🌙 ညOT: {night_ot_hours}

💰 **လစာခွဲခြမ်းမှု:**
   🟢 ပုံမှန်: ¥{regular_salary:,.0f}
   🔵 OT: ¥{ot_salary:,.0f}
   🌙 ညOT: ¥{night_ot_salary:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💵 **စုစုပေါင်းလစာ: ¥{total_salary:,.0f}**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

        return response
    
    def _minutes_to_hours(self, minutes: int) -> str:
        """Convert minutes to hours and minutes format."""
        if minutes == 0:
            return "0မိနစ်"
        
        hours = minutes // 60
        mins = minutes % 60
        
        if hours > 0 and mins > 0:
            return f"{hours}နာရီ {mins}မိနစ်"
        elif hours > 0:
            return f"{hours}နာရီ"
        else:
            return f"{mins}မိနစ်"
