"""Goal tracking system for salary and work hour targets."""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from data_storage import DataStorage


class GoalTracker:
    """Handle goal setting and tracking functionality."""

    def __init__(self):
        self.storage = DataStorage()
        self.goals_file = "goals.json"

    def ensure_goals_file(self):
        """Ensure goals file exists."""
        try:
            with open(self.goals_file, 'r', encoding='utf-8') as f:
                pass
        except FileNotFoundError:
            with open(self.goals_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2, ensure_ascii=False)

    def load_goals(self) -> Dict:
        """Load user goals."""
        self.ensure_goals_file()
        try:
            with open(self.goals_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def save_goals(self, goals: Dict) -> bool:
        """Save user goals."""
        try:
            with open(self.goals_file, 'w', encoding='utf-8') as f:
                json.dump(goals, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False

    def set_monthly_goal(self, user_id: str, goal_type: str, target_value: float) -> Dict:
        """Set monthly goal (salary or hours)."""
        try:
            goals = self.load_goals()

            if user_id not in goals:
                goals[user_id] = {}

            current_month = datetime.now().strftime('%Y-%m')

            if 'monthly' not in goals[user_id]:
                goals[user_id]['monthly'] = {}

            if current_month not in goals[user_id]['monthly']:
                goals[user_id]['monthly'][current_month] = {}

            goals[user_id]['monthly'][current_month][goal_type] = {
                'target': target_value,
                'set_date': datetime.now().isoformat(),
                'achieved': False
            }

            success = self.save_goals(goals)

            if success:
                if goal_type == 'salary':
                    return {
                        'success': True,
                        'message': f'လစဉ်လစာပန်းတိုင် ¥{target_value:,.0f} သတ်မှတ်ပြီးပါပြီ။'
                    }
                elif goal_type == 'hours':
                    return {
                        'success': True,
                        'message': f'လစဉ်အလုပ်ချိန်ပန်းတိုင် {target_value} နာရီ သတ်မှတ်ပြီးပါပြီ။'
                    }
                else:
                    return {
                        'success': True,
                        'message': f'လစဉ်ပန်းတိုင် {target_value} သတ်မှတ်ပြီးပါပြီ။'
                    }
            else:
                return {'error': 'ပန်းတိုင် သိမ်းဆည်းရာတွင် အမှားရှိသည်။'}

        except Exception as e:
            return {'error': 'ပန်းတိုင် သတ်မှတ်ရာတွင် အမှားရှိသည်။'}

    def set_weekly_goal(self, user_id: str, goal_type: str, target_value: float) -> Dict:
        """Set weekly goal (salary or hours)."""
        try:
            goals = self.load_goals()

            if user_id not in goals:
                goals[user_id] = {}

            # Get current week (Monday as start)
            today = datetime.now().date()
            days_since_monday = today.weekday()
            monday = today - timedelta(days=days_since_monday)
            week_key = monday.strftime('%Y-W%U')

            if 'weekly' not in goals[user_id]:
                goals[user_id]['weekly'] = {}

            if week_key not in goals[user_id]['weekly']:
                goals[user_id]['weekly'][week_key] = {}

            goals[user_id]['weekly'][week_key][goal_type] = {
                'target': target_value,
                'set_date': datetime.now().isoformat(),
                'achieved': False
            }

            success = self.save_goals(goals)

            if success:
                if goal_type == 'salary':
                    return {
                        'success': True,
                        'message': f'အပတ်စဉ်လစာပန်းတိုင် ¥{target_value:,.0f} သတ်မှတ်ပြီးပါပြီ။'
                    }
                elif goal_type == 'hours':
                    return {
                        'success': True,
                        'message': f'အပတ်စဉ်အလုပ်ချိန်ပန်းတိုင် {target_value} နာရီ သတ်မှတ်ပြီးပါပြီ။'
                    }
                else:
                    return {
                        'success': True,
                        'message': f'အပတ်စဉ်ပန်းတိုင် {target_value} သတ်မှတ်ပြီးပါပြီ။'
                    }
            else:
                return {'error': 'ပန်းတိုင် သိမ်းဆည်းရာတွင် အမှားရှိသည်။'}

        except Exception as e:
            return {'error': 'ပန်းတိုင် သတ်မှတ်ရာတွင် အမှားရှိသည်။'}

    def check_goal_progress(self, user_id: str, period: str = 'monthly') -> Dict:
        """Check progress towards goals."""
        try:
            goals = self.load_goals()

            if user_id not in goals or period not in goals[user_id]:
                return {'error': 'ပန်းတိုင် မသတ်မှတ်ထားပါ။'}

            if period == 'monthly':
                current_month = datetime.now().strftime('%Y-%m')
                if current_month not in goals[user_id]['monthly']:
                    return {'error': 'ဤလအတွက် ပန်းတိုင် မသတ်မှတ်ထားပါ။'}

                # Get monthly data
                monthly_data = self.storage.get_date_range_data(user_id, 31)

                if not monthly_data or not monthly_data.get('calculations'):
                    return {'error': 'ဤလအတွက် ဒေတာ မတွေ့ပါ။'}

                # Filter for current month
                current_month_data = {}
                for date_str, calculations in monthly_data['calculations'].items():
                    if date_str.startswith(current_month):
                        current_month_data[date_str] = calculations

                # Calculate current totals
                current_salary = 0
                current_hours = 0

                for calculations in current_month_data.values():
                    for calc in calculations:
                        current_salary += calc['total_salary']
                        current_hours += calc['total_minutes'] / 60

                # Get goals for current month
                month_goals = goals[user_id]['monthly'][current_month]

                progress = {}
                for goal_type, goal_data in month_goals.items():
                    target = goal_data['target']

                    if goal_type == 'salary':
                        current_value = current_salary
                        progress[goal_type] = {
                            'current': current_value,
                            'target': target,
                            'progress_percent': (current_value / target * 100) if target > 0 else 0,
                            'remaining': max(0, target - current_value),
                            'achieved': current_value >= target
                        }
                    elif goal_type == 'hours':
                        current_value = current_hours
                        progress[goal_type] = {
                            'current': current_value,
                            'target': target,
                            'progress_percent': (current_value / target * 100) if target > 0 else 0,
                            'remaining': max(0, target - current_value),
                            'achieved': current_value >= target
                        }

                return {
                    'period': 'monthly',
                    'month': current_month,
                    'progress': progress,
                    'days_worked': len(current_month_data),
                    'days_remaining': (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1) - datetime.now().date()
                }

            elif period == 'weekly':
                # Get current week
                today = datetime.now().date()
                days_since_monday = today.weekday()
                monday = today - timedelta(days=days_since_monday)
                week_key = monday.strftime('%Y-W%U')

                if week_key not in goals[user_id]['weekly']:
                    return {'error': 'ဤအပတ်အတွက် ပန်းတိုင် မသတ်မှတ်ထားပါ။'}

                # Get weekly data
                weekly_data = self.storage.get_date_range_data(user_id, 7)

                if not weekly_data or not weekly_data.get('calculations'):
                    return {'error': 'ဤအပတ်အတွက် ဒေတာ မတွေ့ပါ။'}

                # Calculate current totals
                current_salary = 0
                current_hours = 0

                for calculations in weekly_data['calculations'].values():
                    for calc in calculations:
                        current_salary += calc['total_salary']
                        current_hours += calc['total_minutes'] / 60

                # Get goals for current week
                week_goals = goals[user_id]['weekly'][week_key]

                progress = {}
                for goal_type, goal_data in week_goals.items():
                    target = goal_data['target']

                    if goal_type == 'salary':
                        current_value = current_salary
                        progress[goal_type] = {
                            'current': current_value,
                            'target': target,
                            'progress_percent': (current_value / target * 100) if target > 0 else 0,
                            'remaining': max(0, target - current_value),
                            'achieved': current_value >= target
                        }
                    elif goal_type == 'hours':
                        current_value = current_hours
                        progress[goal_type] = {
                            'current': current_value,
                            'target': target,
                            'progress_percent': (current_value / target * 100) if target > 0 else 0,
                            'remaining': max(0, target - current_value),
                            'achieved': current_value >= target
                        }

                return {
                    'period': 'weekly',
                    'week': week_key,
                    'progress': progress,
                    'days_worked': len(weekly_data['calculations']),
                    'days_remaining': 7 - today.weekday()
                }

            return {'error': 'မမှန်ကန်သောကာလ။'}

        except Exception as e:
            return {'error': 'ပန်းတိုင်တိုးတက်မှု စစ်ဆေးရာတွင် အမှားရှိသည်။'}

    def get_achievement_summary(self, user_id: str) -> Dict:
        """Get summary of achieved goals."""
        try:
            goals = self.load_goals()

            if user_id not in goals:
                return {'monthly_achieved': 0, 'weekly_achieved': 0, 'total_goals': 0}

            monthly_achieved = 0
            weekly_achieved = 0
            total_goals = 0

            # Count monthly achievements
            if 'monthly' in goals[user_id]:
                for month_data in goals[user_id]['monthly'].values():
                    for goal_data in month_data.values():
                        total_goals += 1
                        if goal_data.get('achieved', False):
                            monthly_achieved += 1

            # Count weekly achievements
            if 'weekly' in goals[user_id]:
                for week_data in goals[user_id]['weekly'].values():
                    for goal_data in week_data.values():
                        total_goals += 1
                        if goal_data.get('achieved', False):
                            weekly_achieved += 1

            return {
                'monthly_achieved': monthly_achieved,
                'weekly_achieved': weekly_achieved,
                'total_goals': total_goals,
                'achievement_rate': (monthly_achieved + weekly_achieved) / total_goals * 100 if total_goals > 0 else 0
            }

        except Exception as e:
            return {'error': 'အောင်မြင်မှုအကျဉ်းချုပ် ရယူရာတွင် အမှားရှိသည်။'}

    def get_goal_recommendations(self, user_id: str) -> Dict:
        """Get personalized goal recommendations based on history."""
        try:
            # Get last 30 days data
            data = self.storage.get_date_range_data(user_id, 30)

            if not data or not data.get('calculations'):
                return {'recommendations': ['ပထမဆုံး အလုပ်ချိန်မှတ်သားပြီးမှ ပန်းတိုင်သတ်မှတ်ပါ။']}

            # Calculate averages
            total_days = len(data['calculations'])
            total_salary = 0
            total_hours = 0

            for calculations in data['calculations'].values():
                for calc in calculations:
                    total_salary += calc['total_salary']
                    total_hours += calc['total_minutes'] / 60

            avg_daily_salary = total_salary / total_days if total_days > 0 else 0
            avg_daily_hours = total_hours / total_days if total_days > 0 else 0

            # Generate recommendations
            recommendations = []

            # Monthly salary recommendation (slightly higher than current average)
            recommended_monthly_salary = avg_daily_salary * 22 * 1.1  # 22 working days, 10% increase
            recommendations.append(f'လစဉ်လစာပန်းတိုင်: ¥{recommended_monthly_salary:,.0f}')

            # Monthly hours recommendation
            recommended_monthly_hours = avg_daily_hours * 22 * 1.05  # 5% increase
            recommendations.append(f'လစဉ်အလုပ်ချိန်ပန်းတိုင်: {recommended_monthly_hours:.0f} နာရီ')

            # Weekly recommendations
            recommended_weekly_salary = avg_daily_salary * 5 * 1.1  # 5 working days, 10% increase
            recommendations.append(f'အပတ်စဉ်လစာပန်းတိုင်: ¥{recommended_weekly_salary:,.0f}')

            recommended_weekly_hours = avg_daily_hours * 5 * 1.05  # 5% increase
            recommendations.append(f'အပတ်စဉ်အလုပ်ချိန်ပန်းတိုင်: {recommended_weekly_hours:.0f} နာရီ')

            return {
                'recommendations': recommendations,
                'based_on_days': total_days,
                'current_avg_daily_salary': avg_daily_salary,
                'current_avg_daily_hours': avg_daily_hours
            }

        except Exception as e:
            return {'error': 'ပန်းတိုင်အကြံပြုချက်များ ရယူရာတွင် အမှားရှိသည်။'}
import json
import os
from datetime import datetime, date
from typing import Dict, List, Optional
from data_storage import DataStorage

class GoalTracker:
    """Handle goal tracking and progress monitoring."""

    def __init__(self, goals_file: str = "goals.json"):
        self.goals_file = goals_file
        self.storage = DataStorage()
        self.ensure_goals_file()

    def ensure_goals_file(self):
        """Ensure goals file exists."""
        if not os.path.exists(self.goals_file):
            with open(self.goals_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    def load_goals(self) -> Dict:
        """Load goals data."""
        try:
            with open(self.goals_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def save_goals(self, goals: Dict) -> bool:
        """Save goals data."""
        try:
            with open(self.goals_file, 'w', encoding='utf-8') as f:
                json.dump(goals, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False

    def set_monthly_goal(self, user_id: str, goal_type: str, target: float) -> Dict:
        """Set monthly goal for user."""
        try:
            if goal_type not in ['salary', 'hours']:
                return {'error': 'ပန်းတိုင်အမျိုးအစား မမှန်ကန်ပါ (salary သို့မဟုတ် hours)'}

            goals = self.load_goals()
            current_month = datetime.now().strftime('%Y-%m')

            if user_id not in goals:
                goals[user_id] = {}

            if 'monthly' not in goals[user_id]:
                goals[user_id]['monthly'] = {}

            if current_month not in goals[user_id]['monthly']:
                goals[user_id]['monthly'][current_month] = {}

            goals[user_id]['monthly'][current_month][goal_type] = {
                'target': target,
                'set_date': datetime.now().isoformat()
            }

            if self.save_goals(goals):
                unit = '¥' if goal_type == 'salary' else 'နာရီ'
                return {
                    'success': True,
                    'message': f'လစဉ်{goal_type}ပန်းတိုင် {target:,.0f}{unit} သတ်မှတ်ပြီးပါပြီ'
                }
            else:
                return {'error': 'ပန်းတိုင်သိမ်းဆည်းရာတွင် အမှားရှိခဲ့သည်'}

        except Exception as e:
            return {'error': f'ပန်းတိုင်သတ်မှတ်ရာတွင် အမှားရှိခဲ့သည်: {str(e)}'}

    def check_goal_progress(self, user_id: str, period: str = 'monthly') -> dict:
        """Check progress towards goals for a given period."""
        try:
            goals = self.load_goals()

            if user_id not in goals or period not in goals[user_id]:
                return {'error': 'ပန်းတိုင် မသတ်မှတ်ထားပါ။'}

            if period == 'monthly':
                current_month = datetime.now().strftime('%Y-%m')
                if current_month not in goals[user_id]['monthly']:
                    return {'error': 'ဤလအတွက် ပန်းတိုင် မသတ်မှတ်ထားပါ။'}

                # Get monthly data
                monthly_data = self.storage.get_date_range_data(user_id, 31)

                if not monthly_data or not monthly_data.get('calculations'):
                    return {'error': 'ဤလအတွက် ဒေတာ မတွေ့ပါ။'}

                # Filter for current month
                current_month_data = {}
                for date_str, calculations in monthly_data['calculations'].items():
                    if date_str.startswith(current_month):
                        current_month_data[date_str] = calculations

                # Calculate current totals
                current_salary = 0
                current_hours = 0

                for calculations in current_month_data.values():
                    for calc in calculations:
                        current_salary += calc['total_salary']
                        current_hours += calc['total_minutes'] / 60

                # Get goals for current month
                month_goals = goals[user_id]['monthly'][current_month]

                progress = {}
                for goal_type, goal_data in month_goals.items():
                    target = goal_data['target']

                    if goal_type == 'salary':
                        current_value = current_salary
                        progress[goal_type] = {
                            'current': current_value,
                            'target': target,
                            'progress_percent': (current_value / target * 100) if target > 0 else 0,
                            'remaining': max(0, target - current_value),
                            'achieved': current_value >= target
                        }
                    elif goal_type == 'hours':
                        current_value = current_hours
                        progress[goal_type] = {
                            'current': current_value,
                            'target': target,
                            'progress_percent': (current_value / target * 100) if target > 0 else 0,
                            'remaining': max(0, target - current_value),
                            'achieved': current_value >= target
                        }

                return {
                    'period': 'monthly',
                    'month': current_month,
                    'progress': progress,
                    'days_worked': len(current_month_data),
                    'days_remaining': (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1) - datetime.now().date()
                }

            elif period == 'weekly':
                # Get current week
                today = datetime.now().date()
                days_since_monday = today.weekday()
                monday = today - timedelta(days=days_since_monday)
                week_key = monday.strftime('%Y-W%U')

                if week_key not in goals[user_id]['weekly']:
                    return {'error': 'ဤအပတ်အတွက် ပန်းတိုင် မသတ်မှတ်ထားပါ။'}

                # Get weekly data
                weekly_data = self.storage.get_date_range_data(user_id, 7)

                if not weekly_data or not weekly_data.get('calculations'):
                    return {'error': 'ဤအပတ်အတွက် ဒေတာ မတွေ့ပါ။'}

                # Calculate current totals
                current_salary = 0
                current_hours = 0

                for calculations in weekly_data['calculations'].values():
                    for calc in calculations:
                        current_salary += calc['total_salary']
                        current_hours += calc['total_minutes'] / 60

                # Get goals for current week
                week_goals = goals[user_id]['weekly'][week_key]

                progress = {}
                for goal_type, goal_data in week_goals.items():
                    target = goal_data['target']

                    if goal_type == 'salary':
                        current_value = current_salary
                        progress[goal_type] = {
                            'current': current_value,
                            'target': target,
                            'progress_percent': (current_value / target * 100) if target > 0 else 0,
                            'remaining': max(0, target - current_value),
                            'achieved': current_value >= target
                        }
                    elif goal_type == 'hours':
                        current_value = current_hours
                        progress[goal_type] = {
                            'current': current_value,
                            'target': target,
                            'progress_percent': (current_value / target * 100) if target > 0 else 0,
                            'remaining': max(0, target - current_value),
                            'achieved': current_value >= target
                        }

                return {
                    'period': 'weekly',
                    'week': week_key,
                    'progress': progress,
                    'days_worked': len(weekly_data['calculations']),
                    'days_remaining': 7 - today.weekday()
                }

            return {'error': 'မမှန်ကန်သောကာလ။'}

        except Exception as e:
            return {'error': 'ပန်းတိုင်တိုးတက်မှု စစ်ဆေးရာတွင် အမှားရှိသည်။'}

    def get_achievement_summary(self, user_id: str) -> Dict:
        """Get summary of achieved goals."""
        try:
            goals = self.load_goals()

            if user_id not in goals:
                return {'monthly_achieved': 0, 'weekly_achieved': 0, 'total_goals': 0}

            monthly_achieved = 0
            weekly_achieved = 0
            total_goals = 0

            # Count monthly achievements
            if 'monthly' in goals[user_id]:
                for month_data in goals[user_id]['monthly'].values():
                    for goal_data in month_data.values():
                        total_goals += 1
                        if goal_data.get('achieved', False):
                            monthly_achieved += 1

            # Count weekly achievements
            if 'weekly' in goals[user_id]:
                for week_data in goals[user_id]['weekly'].values():
                    for goal_data in week_data.values():
                        total_goals += 1
                        if goal_data.get('achieved', False):
                            weekly_achieved += 1

            return {
                'monthly_achieved': monthly_achieved,
                'weekly_achieved': weekly_achieved,
                'total_goals': total_goals,
                'achievement_rate': (monthly_achieved + weekly_achieved) / total_goals * 100 if total_goals > 0 else 0
            }

        except Exception as e:
            return {'error': 'အောင်မြင်မှုအကျဉ်းချုပ် ရယူရာတွင် အမှားရှိသည်။'}

    def get_goal_recommendations(self, user_id: str) -> Dict:
        """Get personalized goal recommendations based on history."""
        try:
            # Get last 30 days data
            data = self.storage.get_date_range_data(user_id, 30)

            if not data or not data.get('calculations'):
                return {'recommendations': ['ပထမဆုံး အလုပ်ချိန်မှတ်သားပြီးမှ ပန်းတိုင်သတ်မှတ်ပါ။']}

            # Calculate averages
            total_days = len(data['calculations'])
            total_salary = 0
            total_hours = 0

            for calculations in data['calculations'].values():
                for calc in calculations:
                    total_salary += calc['total_salary']
                    total_hours += calc['total_minutes'] / 60

            avg_daily_salary = total_salary / total_days if total_days > 0 else 0
            avg_daily_hours = total_hours / total_days if total_days > 0 else 0

            # Generate recommendations
            recommendations = []

            # Monthly salary recommendation (slightly higher than current average)
            recommended_monthly_salary = avg_daily_salary * 22 * 1.1  # 22 working days, 10% increase
            recommendations.append(f'လစဉ်လစာပန်းတိုင်: ¥{recommended_monthly_salary:,.0f}')

            # Monthly hours recommendation
            recommended_monthly_hours = avg_daily_hours * 22 * 1.05  # 5% increase
            recommendations.append(f'လစဉ်အလုပ်ချိန်ပန်းတိုင်: {recommended_monthly_hours:.0f} နာရီ')

            # Weekly recommendations
            recommended_weekly_salary = avg_daily_salary * 5 * 1.1  # 5 working days, 10% increase
            recommendations.append(f'အပတ်စဉ်လစာပန်းတိုင်: ¥{recommended_weekly_salary:,.0f}')

            recommended_weekly_hours = avg_daily_hours * 5 * 1.05  # 5% increase
            recommendations.append(f'အပတ်စဉ်အလုပ်ချိန်ပန်းတိုင်: {recommended_weekly_hours:.0f} နာရီ')

            return {
                'recommendations': recommendations,
                'based_on_days': total_days,
                'current_avg_daily_salary': avg_daily_salary,
                'current_avg_daily_hours': avg_daily_hours
            }

        except Exception as e:
            return {'error': 'ပန်းတိုင်အကြံပြုချက်များ ရယူရာတွင် အမှားရှိသည်။'}
import json
import os
from datetime import datetime, date
from typing import Dict, List, Optional
from data_storage import DataStorage

class GoalTracker:
    """Handle goal tracking and progress monitoring."""

    def __init__(self, goals_file: str = "goals.json"):
        self.goals_file = goals_file
        self.storage = DataStorage()
        self.ensure_goals_file()

    def ensure_goals_file(self):
        """Ensure goals file exists."""
        if not os.path.exists(self.goals_file):
            with open(self.goals_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    def load_goals(self) -> Dict:
        """Load goals data."""
        try:
            with open(self.goals_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def save_goals(self, goals: Dict) -> bool:
        """Save goals data."""
        try:
            with open(self.goals_file, 'w', encoding='utf-8') as f:
                json.dump(goals, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False

    def set_monthly_goal(self, user_id: str, goal_type: str, target: float) -> Dict:
        """Set monthly goal for user."""
        try:
            if goal_type not in ['salary', 'hours']:
                return {'error': 'ပန်းတိုင်အမျိုးအစား မမှန်ကန်ပါ (salary သို့မဟုတ် hours)'}

            goals = self.load_goals()
            current_month = datetime.now().strftime('%Y-%m')

            if user_id not in goals:
                goals[user_id] = {}

            if 'monthly' not in goals[user_id]:
                goals[user_id]['monthly'] = {}

            if current_month not in goals[user_id]['monthly']:
                goals[user_id]['monthly'][current_month] = {}

            goals[user_id]['monthly'][current_month][goal_type] = {
                'target': target,
                'set_date': datetime.now().isoformat()
            }

            if self.save_goals(goals):
                unit = '¥' if goal_type == 'salary' else 'နာရီ'
                return {
                    'success': True,
                    'message': f'လစဉ်{goal_type}ပန်းတိုင် {target:,.0f}{unit} သတ်မှတ်ပြီးပါပြီ'
                }
            else:
                return {'error': 'ပန်းတိုင်သိမ်းဆည်းရာတွင် အမှားရှိခဲ့သည်'}

        except Exception as e:
            return {'error': f'ပန်းတိုင်သတ်မှတ်ရာတွင် အမှားရှိခဲ့သည်: {str(e)}'}

    def check_goal_progress(self, user_id: str, period: str = 'monthly') -> dict:
        """Check progress towards goals for a given period."""
        try:
            goals = self.load_goals()

            if user_id not in goals or period not in goals[user_id]:
                return {'error': 'ပန်းတိုင် မသတ်မှတ်ထားပါ။'}

            if period == 'monthly':
                current_month = datetime.now().strftime('%Y-%m')
                if current_month not in goals[user_id]['monthly']:
                    return {'error': 'ဤလအတွက် ပန်းတိုင် မသတ်မှတ်ထားပါ။'}

                # Get monthly data
                monthly_data = self.storage.get_date_range_data(user_id, 31)

                if not monthly_data or not monthly_data.get('calculations'):
                    return {'error': 'ဤလအတွက် ဒေတာ မတွေ့ပါ။'}

                # Filter for current month
                current_month_data = {}
                for date_str, calculations in monthly_data['calculations'].items():
                    if date_str.startswith(current_month):
                        current_month_data[date_str] = calculations

                # Calculate current totals
                current_salary = 0
                current_hours = 0

                for calculations in current_month_data.values():
                    for calc in calculations:
                        current_salary += calc['total_salary']
                        current_hours += calc['total_minutes'] / 60

                # Get goals for current month
                month_goals = goals[user_id]['monthly'][current_month]

                progress = {}
                for goal_type, goal_data in month_goals.items():
                    target = goal_data['target']

                    if goal_type == 'salary':
                        current_value = current_salary
                        progress[goal_type] = {
                            'current': current_value,
                            'target': target,
                            'progress_percent': (current_value / target * 100) if target > 0 else 0,
                            'remaining': max(0, target - current_value),
                            'achieved': current_value >= target
                        }
                    elif goal_type == 'hours':
                        current_value = current_hours
                        progress[goal_type] = {
                            'current': current_value,
                            'target': target,
                            'progress_percent': (current_value / target * 100) if target > 0 else 0,
                            'remaining': max(0, target - current_value),
                            'achieved': current_value >= target
                        }

                return {
                    'period': 'monthly',
                    'month': current_month,
                    'progress': progress,
                    'days_worked': len(current_month_data),
                    'days_remaining': (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1) - datetime.now().date()
                }

            elif period == 'weekly':
                # Get current week
                today = datetime.now().date()
                days_since_monday = today.weekday()
                monday = today - timedelta(days=days_since_monday)
                week_key = monday.strftime('%Y-W%U')

                if week_key not in goals[user_id]['weekly']:
                    return {'error': 'ဤအပတ်အတွက် ပန်းတိုင် မသတ်မှတ်ထားပါ။'}

                # Get weekly data
                weekly_data = self.storage.get_date_range_data(user_id, 7)

                if not data or not weekly_data.get('calculations'):
                    return {'error': 'ဤအပတ်အတွက် ဒေတာ မတွေ့ပါ။'}

                # Calculate current totals
                current_salary = 0
                current_hours = 0

                for calculations in weekly_data['calculations'].values():
                    for calc in calculations:
                        current_salary += calc['total_salary']
                        current_hours += calc['total_minutes'] / 60

                # Get goals for current week
                week_goals = goals[user_id]['weekly'][week_key]

                progress = {}
                for goal_type, goal_data in week_goals.items():
                    target = goal_data['target']

                    if goal_type == 'salary':
                        current_value = current_salary
                        progress[goal_type] = {
                            'current': current_value,
                            'target': target,
                            'progress_percent': (current_value / target * 100) if target > 0 else 0,
                            'remaining': max(0, target - current_value),
                            'achieved': current_value >= target
                        }
                    elif goal_type == 'hours':
                        current_value = current_hours
                        progress[goal_type] = {
                            'current': current_value,
                            'target': target,
                            'progress_percent': (current_value / target * 100) if target > 0 else 0,
                            'remaining': max(0, target - current_value),
                            'achieved': current_value >= target
                        }

                return {
                    'period': 'weekly',
                    'week': week_key,
                    'progress': progress,
                    'days_worked': len(weekly_data['calculations']),
                    'days_remaining': 7 - today.weekday()
                }

            return {'error': 'မမှန်ကန်သောကာလ။'}

        except Exception as e:
            return {'error': 'ပန်းတိုင်တိုးတက်မှု စစ်ဆေးရာတွင် အမှားရှိသည်။'}

    def get_achievement_summary(self, user_id: str) -> Dict:
        """Get summary of achieved goals."""
        try:
            goals = self.load_goals()

            if user_id not in goals:
                return {'monthly_achieved': 0, 'weekly_achieved': 0, 'total_goals': 0}

            monthly_achieved = 0
            weekly_achieved = 0
            total_goals = 0

            # Count monthly achievements
            if 'monthly' in goals[user_id]:
                for month_data in goals[user_id]['monthly'].values():
                    for goal_data in month_data.values():
                        total_goals += 1
                        if goal_data.get('achieved', False):
                            monthly_achieved += 1

            # Count weekly achievements
            if 'weekly' in goals[user_id]:
                for week_data in goals[user_id]['weekly'].values():
                    for goal_data in week_data.values():
                        total_goals += 1
                        if goal_data.get('achieved', False):
                            weekly_achieved += 1

            return {
                'monthly_achieved': monthly_achieved,
                'weekly_achieved': weekly_achieved,
                'total_goals': total_goals,
                'achievement_rate': (monthly_achieved + weekly_achieved) / total_goals * 100 if total_goals > 0 else 0
            }

        except Exception as e:
            return {'error': 'အောင်မြင်မှုအကျဉ်းချုပ် ရယူရာတွင် အမှားရှိသည်။'}

    def get_goal_recommendations(self, user_id: str) -> Dict:
        """Get personalized goal recommendations based on history."""
        try:
            # Get last 30 days data
            data = self.storage.get_date_range_data(user_id, 30)

            if not data or not data.get('calculations'):
                return {'recommendations': ['ပထမဆုံး အလုပ်ချိန်မှတ်သားပြီးမှ ပန်းတိုင်သတ်မှတ်ပါ။']}

            # Calculate averages
            total_days = len(data['calculations'])
            total_salary = 0
            total_hours = 0

            for calculations in data['calculations'].values():
                for calc in calculations:
                    total_salary += calc['total_salary']
                    total_hours += calc['total_minutes'] / 60

            avg_daily_salary = total_salary / total_days if total_days > 0 else 0
            avg_daily_hours = total_hours / total_days if total_days > 0 else 0

            # Generate recommendations
            recommendations = []

            # Monthly salary recommendation (slightly higher than current average)
            recommended_monthly_salary = avg_daily_salary * 22 * 1.1  # 22 working days, 10% increase
            recommendations.append(f'လစဉ်လစာပန်းတိုင်: ¥{recommended_monthly_salary:,.0f}')

            # Monthly hours recommendation
            recommended_monthly_hours = avg_daily_hours * 22 * 1.05  # 5% increase
            recommendations.append(f'လစဉ်အလုပ်ချိန်ပန်းတိုင်: {recommended_monthly_hours:.0f} နာရီ')

            # Weekly recommendations
            recommended_weekly_salary = avg_daily_salary * 5 * 1.1  # 5 working days, 10% increase
            recommendations.append(f'အပတ်စဉ်လစာပန်းတိုင်: ¥{recommended_weekly_salary:,.0f}')

            recommended_weekly_hours = avg_daily_hours * 5 * 1.05  # 5% increase
            recommendations.append(f'အပတ်စဉ်အလုပ်ချိန်ပန်းတိုင်: {recommended_weekly_hours:.0f} နာရီ')

            return {
                'recommendations': recommendations,
                'based_on_days': total_days,
                'current_avg_daily_salary': avg_daily_salary,
                'current_avg_daily_hours': avg_daily_hours
            }

        except Exception as e:
            return {'error': 'ပန်းတိုင်အကြံပြုချက်များ ရယူရာတွင် အမှားရှိသည်။'}

    def delete_all_goals(self, user_id: str) -> bool:
        """Delete all goals for a specific user."""
        try:
            goals = self.load_goals()
            if user_id in goals:
                del goals[user_id]
                success = self.save_goals(goals)
                if success:
                    return True
                else:
                    return False
            return True  # No goals to delete is also successful

        except Exception as e:
            return False
# This code merges the changes from the change snippet into the original code, including the new method and replacing the check_goal_progress function.