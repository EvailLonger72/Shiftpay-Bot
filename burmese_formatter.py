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

        # Format salary breakdown with proper Burmese formatting and new OT rates
        salary_breakdown = f"""
💸 **လစာခွဲခြမ်းစိတ်ဖြာမှု:**
   💚 ပုံမှန် ({regular_hours} နာရီ x ¥2,100): ¥{regular_salary:,.0f}
   🔴 OT ({ot_hours + night_ot_hours} နာရီ x ¥2,625): ¥{ot_salary + night_ot_salary:,.0f}

💰 **စုစုပေါင်းလစာ: ¥{total_salary:,.0f}**

⚡ **OT နှုန်း:** 7:35 ကျော်လွန်ချက် သို့မဟုတ် ညကျော်လျှင် ¥2,625/နာရီ
"""

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