"""Notification system for salary tracking reminders and alerts."""

import json
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional
from data_storage import DataStorage


class NotificationManager:
    """Handle notification and reminder functionality."""
    
    def __init__(self):
        self.storage = DataStorage()
        self.notifications_file = "notifications.json"
    
    def ensure_notifications_file(self):
        """Ensure notifications file exists."""
        try:
            with open(self.notifications_file, 'r', encoding='utf-8') as f:
                pass
        except FileNotFoundError:
            with open(self.notifications_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2, ensure_ascii=False)
    
    def load_notifications(self) -> Dict:
        """Load notification settings."""
        self.ensure_notifications_file()
        try:
            with open(self.notifications_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def save_notifications(self, notifications: Dict) -> bool:
        """Save notification settings."""
        try:
            with open(self.notifications_file, 'w', encoding='utf-8') as f:
                json.dump(notifications, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False
    
    def set_work_reminder(self, user_id: str, reminder_time: str, message: str = None) -> Dict:
        """Set daily work reminder."""
        try:
            # Validate time format
            time_obj = datetime.strptime(reminder_time, '%H:%M').time()
            
            notifications = self.load_notifications()
            
            if user_id not in notifications:
                notifications[user_id] = {}
            
            notifications[user_id]['work_reminder'] = {
                'time': reminder_time,
                'message': message or 'အလုပ်ချိန် မှတ်သားရန် မမေ့ပါနှင့်!',
                'enabled': True,
                'created_at': datetime.now().isoformat()
            }
            
            success = self.save_notifications(notifications)
            
            if success:
                return {
                    'success': True,
                    'message': f'နေ့စဉ် {reminder_time} တွင် အလုပ်ချိန်သတိပေးချက် သတ်မှတ်ပြီးပါပြီ။'
                }
            else:
                return {'error': 'သတိပေးချက် သိမ်းဆည်းရာတွင် အမှားရှိသည်။'}
                
        except ValueError:
            return {'error': 'အချိန်ပုံစံ မမှန်ကန်ပါ။ (HH:MM ပုံစံဖြင့် ရေးပါ)'}
        except Exception as e:
            return {'error': 'သတိပေးချက် သတ်မှတ်ရာတွင် အမှားရှိသည်။'}
    
    def get_user_notifications(self, user_id: str) -> Dict:
        """Get user's notification settings."""
        notifications = self.load_notifications()
        
        if user_id not in notifications:
            return {'work_reminder': None}
        
        return notifications[user_id]
    
    def disable_reminder(self, user_id: str, reminder_type: str) -> Dict:
        """Disable a specific reminder."""
        try:
            notifications = self.load_notifications()
            
            if user_id not in notifications or reminder_type not in notifications[user_id]:
                return {'error': 'သတိပေးချက် မတွေ့ပါ။'}
            
            notifications[user_id][reminder_type]['enabled'] = False
            
            success = self.save_notifications(notifications)
            
            if success:
                return {'success': True, 'message': 'သတိပေးချက် ပိတ်ပြီးပါပြီ။'}
            else:
                return {'error': 'သတိပေးချက် ပိတ်ရာတွင် အမှားရှိသည်။'}
                
        except Exception as e:
            return {'error': 'သတိပေးချက် ပိတ်ရာတွင် အမှားရှိသည်။'}
    
    def check_missing_entries(self, user_id: str, days: int = 7) -> Dict:
        """Check for missing work entries in recent days."""
        try:
            user_data = self.storage.load_user_data(user_id)
            
            if not user_data:
                return {'missing_days': [], 'total_missing': 0}
            
            # Check last N days
            missing_days = []
            today = datetime.now().date()
            
            for i in range(1, days + 1):
                check_date = today - timedelta(days=i)
                date_str = check_date.isoformat()
                
                # Skip weekends (assuming Saturday=5, Sunday=6)
                if check_date.weekday() >= 5:
                    continue
                
                if date_str not in user_data or not user_data[date_str]:
                    missing_days.append({
                        'date': date_str,
                        'day_name': check_date.strftime('%A'),
                        'burmese_day': self._get_burmese_day(check_date.weekday())
                    })
            
            return {
                'missing_days': missing_days,
                'total_missing': len(missing_days)
            }
            
        except Exception as e:
            return {'error': 'မပြည့်စုံသောရက်များ ရှာရာတွင် အမှားရှိသည်။'}
    
    def _get_burmese_day(self, weekday: int) -> str:
        """Convert weekday to Burmese day name."""
        days = ['တနင်္လာ', 'အင်္ဂါ', 'ဗုဒ္ధဟူး', 'ကြာသပတေး', 'သောကြာ', 'စနေ', 'တနင်္ဂနွေ']
        return days[weekday]
    
    def generate_work_summary_alert(self, user_id: str) -> Dict:
        """Generate work summary alert for low performance."""
        try:
            # Get last 7 days data
            data = self.storage.get_date_range_data(user_id, 7)
            
            if not data or not data.get('calculations'):
                return {'alert': False, 'message': 'ဒေတာ မတွေ့ပါ။'}
            
            # Calculate weekly totals
            total_days = len(data['calculations'])
            total_salary = 0
            total_hours = 0
            
            for calculations in data['calculations'].values():
                for calc in calculations:
                    total_salary += calc['total_salary']
                    total_hours += calc['total_minutes'] / 60
            
            # Check if performance is low
            avg_daily_hours = total_hours / 7 if total_days > 0 else 0
            avg_daily_salary = total_salary / 7 if total_days > 0 else 0
            
            alerts = []
            
            # Less than 3 days worked in a week
            if total_days < 3:
                alerts.append(f'ဤအပတ်တွင် {total_days} ရက်သာ အလုပ်လုပ်ခဲ့သည်။')
            
            # Less than 6 hours average per day
            if avg_daily_hours < 6:
                alerts.append(f'နေ့စဉ်ပျမ်းမျှ {avg_daily_hours:.1f} နာရီသာ အလုပ်လုပ်ခဲ့သည်။')
            
            # Low weekly salary
            if total_salary < 50000:
                alerts.append(f'ဤအပတ်လစာ ¥{total_salary:,.0f} သာရရှိခဲ့သည်။')
            
            if alerts:
                return {
                    'alert': True,
                    'message': '⚠️ အလုပ်စွမ်းအားသတိပေးချက်:\n\n' + '\n'.join(f'• {alert}' for alert in alerts),
                    'suggestions': [
                        'နေ့စဉ် ၈ နာရီ ပြည့်အလုပ်လုပ်ရန်',
                        'အပတ်စဉ် အနည်းဆုံး ၅ ရက် အလုပ်လုပ်ရန်',
                        'OT လုပ်ရန် ယှဉ်ပြိုင်ရန်'
                    ]
                }
            
            return {'alert': False, 'message': 'အလုပ်စွမ်းအား ကောင်းမွန်နေပါသည်။'}
            
        except Exception as e:
            return {'error': 'စွမ်းအားသတိပေးချက် စစ်ဆေးရာတွင် အမှားရှိသည်။'}
    
    def get_streak_info(self, user_id: str) -> Dict:
        """Get work streak information."""
        try:
            user_data = self.storage.load_user_data(user_id)
            
            if not user_data:
                return {'current_streak': 0, 'longest_streak': 0, 'last_work_date': None}
            
            # Sort dates
            sorted_dates = sorted(user_data.keys(), reverse=True)
            
            current_streak = 0
            longest_streak = 0
            temp_streak = 0
            last_work_date = None
            
            if sorted_dates:
                last_work_date = sorted_dates[0]
            
            # Calculate current streak
            today = datetime.now().date()
            current_date = today
            
            for i, date_str in enumerate(sorted_dates):
                work_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # Check if this is consecutive
                if i == 0:
                    if work_date == today or work_date == today - timedelta(days=1):
                        current_streak = 1
                        temp_streak = 1
                    else:
                        current_streak = 0
                        break
                else:
                    prev_date = datetime.strptime(sorted_dates[i-1], '%Y-%m-%d').date()
                    
                    if (prev_date - work_date).days == 1:
                        current_streak += 1
                        temp_streak += 1
                    else:
                        break
            
            # Calculate longest streak
            for i in range(len(sorted_dates)):
                temp_streak = 1
                
                for j in range(i + 1, len(sorted_dates)):
                    prev_date = datetime.strptime(sorted_dates[j-1], '%Y-%m-%d').date()
                    curr_date = datetime.strptime(sorted_dates[j], '%Y-%m-%d').date()
                    
                    if (prev_date - curr_date).days == 1:
                        temp_streak += 1
                    else:
                        break
                
                longest_streak = max(longest_streak, temp_streak)
            
            return {
                'current_streak': current_streak,
                'longest_streak': longest_streak,
                'last_work_date': last_work_date
            }
            
        except Exception as e:
            return {'error': 'အလုပ်လုပ်ဆက်တိုက်ရက်ရေ ရှာရာတွင် အမှားရှိသည်။'}