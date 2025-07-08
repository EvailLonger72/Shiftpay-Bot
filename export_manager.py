"""Export Manager for salary data export functionality."""

import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from io import StringIO
from data_storage import DataStorage
from time_utils import TimeUtils


class ExportManager:
    """Handle data export functionality for salary calculations."""
    
    def __init__(self):
        self.storage = DataStorage()
        self.time_utils = TimeUtils()
    
    def export_to_csv(self, user_id: str, days: int = 30) -> Optional[str]:
        """Export user data to CSV format."""
        try:
            data = self.storage.get_date_range_data(user_id, days)
            
            if not data or not data.get('calculations'):
                return None
            
            # Create CSV content
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Date', 'Start Time', 'End Time', 'Shift Type', 
                'Total Hours', 'Regular Hours', 'OT Hours', 'Night OT Hours',
                'Total Salary', 'Regular Salary', 'OT Salary', 'Night OT Salary',
                'Break Minutes', 'Paid Minutes'
            ])
            
            # Write data rows
            for date_str, calculations in data['calculations'].items():
                for calc in calculations:
                    writer.writerow([
                        date_str,
                        calc['start_time'],
                        calc['end_time'],
                        calc['shift_type'],
                        round(calc['total_minutes'] / 60, 2),
                        round(calc['regular_minutes'] / 60, 2),
                        round(calc['ot_minutes'] / 60, 2),
                        round(calc['night_ot_minutes'] / 60, 2),
                        calc['total_salary'],
                        calc['regular_salary'],
                        calc['ot_salary'],
                        calc['night_ot_salary'],
                        calc['break_minutes'],
                        calc['paid_minutes']
                    ])
            
            return output.getvalue()
            
        except Exception as e:
            return None
    
    def export_to_json(self, user_id: str, days: int = 30) -> Optional[str]:
        """Export user data to JSON format."""
        try:
            data = self.storage.get_date_range_data(user_id, days)
            
            if not data or not data.get('calculations'):
                return None
            
            # Format data for JSON export
            export_data = {
                'export_date': datetime.now().isoformat(),
                'user_id': user_id,
                'period_days': days,
                'calculations': data['calculations']
            }
            
            return json.dumps(export_data, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return None
    
    def generate_monthly_report(self, user_id: str, month: int, year: int) -> Optional[Dict]:
        """Generate monthly report for specific month/year."""
        try:
            # Get all user data
            user_data = self.storage.load_user_data(user_id)
            
            if not user_data:
                return {'error': 'လူသုံးစွဲသူဒေတာ မတွေ့ပါ။'}
            
            # Filter data for specific month
            monthly_data = {}
            target_month = f"{year:04d}-{month:02d}"
            
            for date_str, calculations in user_data.items():
                if date_str.startswith(target_month):
                    monthly_data[date_str] = calculations
            
            if not monthly_data:
                return {'error': f'{month}/{year} အတွက် ဒေတာမတွေ့ပါ။'}
            
            # Calculate monthly statistics
            total_days = len(monthly_data)
            total_salary = 0
            total_minutes = 0
            total_regular_minutes = 0
            total_ot_minutes = 0
            total_night_ot_minutes = 0
            shift_counts = {}
            
            for calculations in monthly_data.values():
                for calc in calculations:
                    total_salary += calc['total_salary']
                    total_minutes += calc['total_minutes']
                    total_regular_minutes += calc['regular_minutes']
                    total_ot_minutes += calc['ot_minutes']
                    total_night_ot_minutes += calc['night_ot_minutes']
                    
                    shift_type = calc['shift_type']
                    shift_counts[shift_type] = shift_counts.get(shift_type, 0) + 1
            
            # Calculate averages
            avg_daily_salary = total_salary / total_days if total_days > 0 else 0
            avg_daily_hours = (total_minutes / 60) / total_days if total_days > 0 else 0
            
            return {
                'month': month,
                'year': year,
                'total_days': total_days,
                'total_salary': total_salary,
                'total_hours': round(total_minutes / 60, 2),
                'total_regular_hours': round(total_regular_minutes / 60, 2),
                'total_ot_hours': round(total_ot_minutes / 60, 2),
                'total_night_ot_hours': round(total_night_ot_minutes / 60, 2),
                'avg_daily_salary': round(avg_daily_salary, 0),
                'avg_daily_hours': round(avg_daily_hours, 2),
                'shift_counts': shift_counts,
                'daily_breakdown': monthly_data
            }
            
        except Exception as e:
            return {'error': 'လစဉ်အစီရင်ခံစာ ပြုလုပ်ရာတွင် အမှားရှိသည်။'}
    
    def get_export_summary(self, user_id: str, days: int = 30) -> Dict:
        """Get summary of exportable data."""
        try:
            data = self.storage.get_date_range_data(user_id, days)
            
            if not data or not data.get('calculations'):
                return {'error': 'ပို့ရန်ဒေတာ မတွေ့ပါ။'}
            
            total_records = sum(len(calcs) for calcs in data['calculations'].values())
            date_range = {
                'start': min(data['calculations'].keys()),
                'end': max(data['calculations'].keys())
            }
            
            return {
                'total_records': total_records,
                'total_days': len(data['calculations']),
                'date_range': date_range,
                'file_size_estimate': {
                    'csv': f"{total_records * 150} bytes",
                    'json': f"{total_records * 300} bytes"
                }
            }
            
        except Exception as e:
            return {'error': 'ပို့ရန်ဒေတာ အကျဉ်းချုပ် ရယူရာတွင် အမှားရှိသည်။'}
import json
import csv
from io import StringIO
from datetime import datetime
from typing import Dict, List, Optional
from data_storage import DataStorage

class ExportManager:
    """Handle data export functionality."""
    
    def __init__(self):
        self.storage = DataStorage()
    
    def get_export_summary(self, user_id: str, days: int = 30) -> Dict:
        """Get export summary information."""
        try:
            user_data = self.storage.load_user_data(user_id)
            
            if not user_data:
                return {'error': 'ပို့ရန်ဒေတာ မရှိပါ။'}
            
            total_records = sum(len(calcs) if isinstance(calcs, list) else 1 for calcs in user_data.values())
            total_days = len(user_data)
            
            dates = sorted(user_data.keys())
            date_range = {
                'start': dates[0] if dates else 'မရှိ',
                'end': dates[-1] if dates else 'မရှိ'
            }
            
            return {
                'total_records': total_records,
                'total_days': total_days,
                'date_range': date_range
            }
            
        except Exception as e:
            return {'error': f'ပို့မှုအချက်အလက်ရယူရာတွင် အမှားရှိခဲ့သည်: {str(e)}'}
    
    def export_to_csv(self, user_id: str, days: int = 30) -> Optional[str]:
        """Export data to CSV format."""
        try:
            # Get user data directly
            user_data = self.storage.load_user_data(user_id)
            
            if not user_data:
                return None
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                'ရက်စွဲ', 'စချိန်', 'ဆုံးချိန်', 'Shift', 'စုစုပေါင်းမိနစ်',
                'Break မိနစ်', 'လုပ်ငန်းမိနစ်', 'ပုံမှန်နာရီ', 'OT နာရီ', 'ညOT နာရီ',
                'စုစုပေါင်းလစာ', 'ပုံမှန်လစာ', 'OT လစာ', 'ညOT လစာ'
            ])
            
            # Data rows
            for date_str in sorted(user_data.keys()):
                date_calculations = user_data[date_str]
                if isinstance(date_calculations, list):
                    for calc in date_calculations:
                        writer.writerow([
                            date_str,
                            calc.get('start_time', ''),
                            calc.get('end_time', ''),
                            calc.get('shift_type', ''),
                            calc.get('total_minutes', 0),
                            calc.get('break_minutes', 0),
                            calc.get('paid_minutes', 0),
                            round(calc.get('regular_minutes', 0) / 60, 2),
                            round(calc.get('ot_minutes', 0) / 60, 2),
                            round(calc.get('night_ot_minutes', 0) / 60, 2),
                            calc.get('total_salary', 0),
                            calc.get('regular_salary', 0),
                            calc.get('ot_salary', 0),
                            calc.get('night_ot_salary', 0)
                        ])
            
            return output.getvalue()
            
        except Exception as e:
            print(f"CSV export error: {e}")
            return None
    
    def export_to_json(self, user_id: str, days: int = 30) -> Optional[str]:
        """Export data to JSON format."""
        try:
            # Get user data directly
            user_data = self.storage.load_user_data(user_id)
            
            if not user_data:
                return None
            
            export_data = {
                'user_id': user_id,
                'export_date': datetime.now().isoformat(),
                'period_days': days,
                'calculations': user_data
            }
            
            return json.dumps(export_data, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"JSON export error: {e}")
            return None
