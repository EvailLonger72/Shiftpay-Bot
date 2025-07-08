import json
import os
from datetime import datetime, date
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
            
            # Get recent dates
            today = date.today()
            recent_data = {}
            
            for i in range(days):
                check_date = (today - timedelta(days=i)).isoformat()
                if check_date in user_data:
                    recent_data[check_date] = user_data[check_date]
            
            return recent_data
            
        except Exception as e:
            logger.error(f"Error getting date range data: {e}")
            return {}
    
    def delete_user_data(self, user_id: str) -> bool:
        """Delete all data for a user."""
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

# Import timedelta
from datetime import timedelta