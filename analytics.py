from datetime import datetime, date, timedelta
from typing import Dict, List, Tuple
import logging
from data_storage import DataStorage

logger = logging.getLogger(__name__)

class Analytics:
    """Handle analytics and data analysis for salary calculations."""
    
    def __init__(self):
        self.storage = DataStorage()
    
    def generate_summary_stats(self, user_id: str, days: int = 30) -> Dict:
        """Generate summary statistics for the user."""
        try:
            user_data = self.storage.get_date_range_data(user_id, days)
            
            if not user_data:
                return {
                    'error': 'မည်သည့်ဒေတာမှမရှိပါ',
                    'total_days': 0,
                    'total_work_hours': 0,
                    'total_salary': 0,
                    'total_ot_hours': 0,
                    'avg_daily_hours': 0,
                    'avg_daily_salary': 0
                }
            
            total_work_minutes = 0
            total_salary = 0
            total_ot_minutes = 0
            total_regular_minutes = 0
            total_night_ot_minutes = 0
            total_days = len(user_data)
            
            # Calculate totals
            for date_str, day_entries in user_data.items():
                for entry in day_entries:
                    total_work_minutes += entry.get('paid_minutes', 0)
                    total_salary += entry.get('total_salary', 0)
                    total_ot_minutes += entry.get('ot_minutes', 0)
                    total_regular_minutes += entry.get('regular_minutes', 0)
                    total_night_ot_minutes += entry.get('night_ot_minutes', 0)
            
            # Convert to hours
            total_work_hours = total_work_minutes / 60
            total_ot_hours = (total_ot_minutes + total_night_ot_minutes) / 60
            total_regular_hours = total_regular_minutes / 60
            
            # Calculate averages
            avg_daily_hours = total_work_hours / total_days if total_days > 0 else 0
            avg_daily_salary = total_salary / total_days if total_days > 0 else 0
            
            return {
                'error': None,
                'total_days': total_days,
                'total_work_hours': round(total_work_hours, 2),
                'total_regular_hours': round(total_regular_hours, 2),
                'total_ot_hours': round(total_ot_hours, 2),
                'total_salary': round(total_salary, 0),
                'avg_daily_hours': round(avg_daily_hours, 2),
                'avg_daily_salary': round(avg_daily_salary, 0),
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error generating summary stats: {e}")
            return {'error': f'ခွဲခြမ်းစိတ်ဖြာမှုအမှား: {str(e)}'}
    
    def generate_bar_chart_data(self, user_id: str, days: int = 14) -> Dict:
        """Generate data for creating a text-based bar chart."""
        try:
            user_data = self.storage.get_date_range_data(user_id, days)
            
            if not user_data:
                return {'error': 'မည်သည့်ဒေတာမှမရှိပါ'}
            
            # Prepare chart data
            chart_data = []
            today = date.today()
            
            for i in range(days - 1, -1, -1):  # Last N days in chronological order
                check_date = today - timedelta(days=i)
                date_str = check_date.isoformat()
                
                daily_hours = 0
                daily_salary = 0
                
                if date_str in user_data:
                    for entry in user_data[date_str]:
                        daily_hours += entry.get('paid_minutes', 0) / 60
                        daily_salary += entry.get('total_salary', 0)
                
                chart_data.append({
                    'date': check_date.strftime('%m/%d'),
                    'hours': round(daily_hours, 1),
                    'salary': round(daily_salary, 0)
                })
            
            return {
                'error': None,
                'chart_data': chart_data,
                'max_hours': max([d['hours'] for d in chart_data]) if chart_data else 0,
                'max_salary': max([d['salary'] for d in chart_data]) if chart_data else 0
            }
            
        except Exception as e:
            logger.error(f"Error generating chart data: {e}")
            return {'error': f'ဂရပ်ဒေတာအမှား: {str(e)}'}
    
    def create_text_bar_chart(self, chart_data: List[Dict], chart_type: str = 'hours') -> str:
        """Create a text-based bar chart."""
        if not chart_data:
            return "ဒေတာမရှိပါ"
        
        # Determine max value for scaling
        if chart_type == 'hours':
            values = [d['hours'] for d in chart_data]
            title = "📊 **နေ့စဉ်အလုပ်ချိန် (နာရီ)**"
            unit = "h"
        else:  # salary
            values = [d['salary'] for d in chart_data]
            title = "💰 **နေ့စဉ်လစာ (¥)**"
            unit = "¥"
        
        max_value = max(values) if values else 1
        chart_width = 15  # Maximum bar width in characters
        
        chart_lines = [title, ""]
        
        for data_point in chart_data:
            date_str = data_point['date']
            value = data_point[chart_type]
            
            # Calculate bar length
            if max_value > 0:
                bar_length = int((value / max_value) * chart_width)
            else:
                bar_length = 0
            
            # Create bar
            bar = "█" * bar_length + "░" * (chart_width - bar_length)
            
            # Format value
            if chart_type == 'hours':
                value_str = f"{value:.1f}{unit}"
            else:
                value_str = f"{unit}{value:,.0f}"
            
            chart_lines.append(f"{date_str} {bar} {value_str}")
        
        return "\n".join(chart_lines)
    
    def get_recent_history(self, user_id: str, days: int = 7) -> Dict:
        """Get recent work history summary."""
        try:
            user_data = self.storage.get_date_range_data(user_id, days)
            
            if not user_data:
                return {'error': 'မည်သည့်ဒေတာမှမရှိပါ'}
            
            history = []
            for date_str in sorted(user_data.keys(), reverse=True):
                day_entries = user_data[date_str]
                
                daily_total_hours = 0
                daily_total_salary = 0
                daily_ot_hours = 0
                shifts = []
                
                for entry in day_entries:
                    daily_total_hours += entry.get('paid_minutes', 0) / 60
                    daily_total_salary += entry.get('total_salary', 0)
                    daily_ot_hours += (entry.get('ot_minutes', 0) + entry.get('night_ot_minutes', 0)) / 60
                    
                    shift_info = f"{entry.get('start_time', '')}~{entry.get('end_time', '')} ({entry.get('shift_type', '')})"
                    shifts.append(shift_info)
                
                # Parse date for display
                try:
                    date_obj = datetime.fromisoformat(date_str).date()
                    display_date = date_obj.strftime('%m/%d')
                except:
                    display_date = date_str
                
                history.append({
                    'date': display_date,
                    'hours': round(daily_total_hours, 1),
                    'ot_hours': round(daily_ot_hours, 1),
                    'salary': round(daily_total_salary, 0),
                    'shifts': ', '.join(shifts)
                })
            
            return {
                'error': None,
                'history': history
            }
            
        except Exception as e:
            logger.error(f"Error getting recent history: {e}")
            return {'error': f'မှတ်တမ်းအမှား: {str(e)}'}