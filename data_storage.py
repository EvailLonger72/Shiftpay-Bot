import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class DataStorage:
    """Handle storage and retrieval of salary calculation data."""

    def __init__(self, data_file: str = "salary_data.json"):
        self.data_file = data_file
        self.ensure_data_file()

    def ensure_data_file(self):
        """Ensure the data file exists."""
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    def save_calculation(self, user_id: str, calculation_result: Dict) -> bool:
        """Save a salary calculation result for a user."""
        try:
            data = self.load_user_data(user_id)

            # Create entry for today
            today = date.today().isoformat()
            if today not in data:
                data[today] = []

            # Add calculation with timestamp
            calculation_entry = {
                'timestamp': datetime.now().isoformat(),
                'start_time': calculation_result['start_time'].strftime('%H:%M'),
                'end_time': calculation_result['end_time'].strftime('%H:%M'),
                'shift_type': calculation_result['shift_type'],
                'total_minutes': calculation_result['total_minutes'],
                'break_minutes': calculation_result['break_minutes'],
                'paid_minutes': calculation_result['paid_minutes'],
                'regular_minutes': calculation_result['regular_minutes'],
                'ot_minutes': calculation_result['ot_minutes'],
                'night_ot_minutes': calculation_result['night_ot_minutes'],
                'total_salary': calculation_result['total_salary'],
                'regular_salary': calculation_result['regular_salary'],
                'ot_salary': calculation_result['ot_salary'],
                'night_ot_salary': calculation_result['night_ot_salary']
            }

            data[today].append(calculation_entry)

            # Save back to file
            return self.save_user_data(user_id, data)

        except Exception as e:
            logger.error(f"Error saving calculation: {e}")
            return False

    def save_calculation(self, user_id: str, calculation_data: Dict) -> bool:
        """Save calculation result for a user."""
        try:
            user_data = self.load_user_data(user_id)
            today = datetime.now().strftime("%Y-%m-%d")

            if today not in user_data:
                user_data[today] = []

            # Create calculation entry
            calculation_entry = {
                'timestamp': datetime.now().isoformat(),
                'start_time': calculation_data['start_time'].strftime("%H:%M"),
                'end_time': calculation_data['end_time'].strftime("%H:%M"),
                'shift_type': calculation_data['shift_type'],
                'total_minutes': calculation_data['total_minutes'],
                'break_minutes': calculation_data['break_minutes'],
                'paid_minutes': calculation_data['paid_minutes'],
                'regular_minutes': calculation_data['regular_minutes'],
                'ot_minutes': calculation_data['ot_minutes'],
                'night_ot_minutes': calculation_data['night_ot_minutes'],
                'regular_salary': calculation_data['regular_salary'],
                'ot_salary': calculation_data['ot_salary'],
                'night_ot_salary': calculation_data['night_ot_salary'],
                'total_salary': calculation_data['total_salary']
            }

            user_data[today].append(calculation_entry)

            return self.save_user_data(user_id, user_data)

        except Exception as e:
            print(f"Error saving calculation: {e}")
            return False

    def save_calculation_with_date(self, user_id: str, calculation_data: Dict, target_date: str) -> bool:
        """Save calculation result for a user with specific date."""
        try:
            user_data = self.load_user_data(user_id)

            if target_date not in user_data:
                user_data[target_date] = []

            # Create calculation entry
            calculation_entry = {
                'timestamp': datetime.now().isoformat(),
                'start_time': calculation_data['start_time'].strftime("%H:%M"),
                'end_time': calculation_data['end_time'].strftime("%H:%M"),
                'shift_type': calculation_data['shift_type'],
                'total_minutes': calculation_data['total_minutes'],
                'break_minutes': calculation_data['break_minutes'],
                'paid_minutes': calculation_data['paid_minutes'],
                'regular_minutes': calculation_data['regular_minutes'],
                'ot_minutes': calculation_data['ot_minutes'],
                'night_ot_minutes': calculation_data['night_ot_minutes'],
                'regular_salary': calculation_data['regular_salary'],
                'ot_salary': calculation_data['ot_salary'],
                'night_ot_salary': calculation_data['night_ot_salary'],
                'total_salary': calculation_data['total_salary'],
                'calculation_date': target_date
            }

            user_data[target_date].append(calculation_entry)

            return self.save_user_data(user_id, user_data)

        except Exception as e:
            print(f"Error saving calculation with date: {e}")
            return False

    def load_user_data(self, user_id: str) -> Dict:
        """Load all data for a specific user."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
                return all_data.get(user_id, {})
        except Exception as e:
            logger.error(f"Error loading user data: {e}")
            return {}

    def save_user_data(self, user_id: str, user_data: Dict) -> bool:
        """Save all data for a specific user."""
        try:
            # Load all data
            with open(self.data_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)

            # Update user's data
            all_data[user_id] = user_data

            # Save back
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            logger.error(f"Error saving user data: {e}")
            return False

    def get_date_range_data(self, user_id: str, days: int = 30) -> Dict:
        """Get data for the last N days."""
        try:
            user_data = self.load_user_data(user_id)

            if not user_data:
                return {'calculations': {}}

            # Get recent dates
            today = date.today()
            recent_data = {}

            for i in range(days):
                check_date = (today - timedelta(days=i)).isoformat()
                if check_date in user_data:
                    recent_data[check_date] = user_data[check_date]

            return {'calculations': recent_data}

        except Exception as e:
            logger.error(f"Error getting date range data: {e}")
            return {'calculations': {}}

    def delete_user_data(self, user_id: str) -> bool:
        """Delete all data for a specific user."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)

            if user_id in all_data:
                del all_data[user_id]

                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)

                return True

            return False

        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            return False

    def delete_old_data(self, user_id: str, days: int) -> bool:
        """Delete data older than specified days."""
        try:
            user_data = self.load_user_data(user_id)

            if not user_data:
                return True

            cutoff_date = (datetime.now() - timedelta(days=days)).date()

            # Filter out old data
            dates_to_delete = []
            for date_str in user_data.keys():
                try:
                    data_date = datetime.fromisoformat(date_str).date()
                    if data_date < cutoff_date:
                        dates_to_delete.append(date_str)
                except ValueError:
                    continue

            # Delete old dates
            for date_str in dates_to_delete:
                del user_data[date_str]

            return self.save_user_data(user_id, user_data)
        except Exception as e:
            logger.error(f"Error deleting old data: {e}")
            return False

    def delete_date_data(self, user_id: str, date_str: str) -> bool:
        """Delete data for a specific date."""
        try:
            user_data = self.load_user_data(user_id)

            if date_str in user_data:
                del user_data[date_str]
                return self.save_user_data(user_id, user_data)

            return False

        except Exception as e:
            logger.error(f"Error deleting date data: {e}")
            return False

    def delete_work_history(self, user_id: str) -> bool:
        """Delete only work history, keep other data."""
        try:
            user_data = self.load_user_data(user_id)

            # Clear the work history by setting the user's data to an empty dictionary.
            user_data = {}
            return self.save_user_data(user_id, user_data)

        except Exception as e:
            logger.error(f"Error deleting work history: {e}")
            return False

    def get_user_data_summary(self, user_id: str) -> dict:
        """Get summary of user data for display."""
        try:
            user_data = self.load_user_data(user_id)

            if not user_data:
                return {
                    'total_records': 0,
                    'total_days': 0,
                    'first_record': None,
                    'last_record': None,
                    'active_goals': 0,
                    'completed_goals': 0,
                    'events': 0,
                    'monthly_avg_days': 0,
                    'estimated_csv_size': '0KB',
                    'estimated_json_size': '0KB'
                }

            total_records = sum(len(day_data) for day_data in user_data.values())
            total_days = len(user_data)

            # Get date range
            dates = list(user_data.keys())
            first_record = min(dates) if dates else None
            last_record = max(dates) if dates else None

            # Estimate file sizes
            estimated_csv_size = f"{total_records * 150}B"
            estimated_json_size = f"{total_records * 300}B"

            # Calculate monthly average
            if dates:
                try:
                    first_date = datetime.fromisoformat(first_record).date()
                    last_date = datetime.fromisoformat(last_record).date()
                    days_diff = (last_date - first_date).days + 1
                    monthly_avg = (total_days / days_diff * 30) if days_diff > 0 else total_days
                except:
                    monthly_avg = 0
            else:
                monthly_avg = 0

            return {
                'total_records': total_records,
                'total_days': total_days,
                'first_record': first_record,
                'last_record': last_record,
                'active_goals': 0,  # Will be filled by goal_tracker if needed
                'completed_goals': 0,
                'events': 0,  # Will be filled by calendar_manager if needed
                'monthly_avg_days': round(monthly_avg, 1),
                'estimated_csv_size': estimated_csv_size,
                'estimated_json_size': estimated_json_size
            }

        except Exception as e:
            logger.error(f"Error getting user data summary: {e}")
            return {
                'total_records': 0,
                'total_days': 0,
                'first_record': None,
                'last_record': None,
                'active_goals': 0,
                'completed_goals': 0,
                'events': 0,
                'monthly_avg_days': 0,
                'estimated_csv_size': '0KB',
                'estimated_json_size': '0KB'
            }

# Import timedelta
from datetime import timedelta