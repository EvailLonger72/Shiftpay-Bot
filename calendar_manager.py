"""Calendar Manager for scheduling and salary payment tracking."""

import json
import os
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
from dateutil.relativedelta import relativedelta

class CalendarManager:
    """Handle calendar functionality including scheduling and salary payment tracking."""
    
    def __init__(self, calendar_file: str = "calendar_data.json"):
        self.calendar_file = calendar_file
        self.ensure_calendar_file()
    
    def ensure_calendar_file(self):
        """Ensure calendar file exists."""
        if not os.path.exists(self.calendar_file):
            default_data = {
                "users": {},
                "salary_payment_day": 25,
                "global_events": []
            }
            with open(self.calendar_file, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
    
    def load_calendar_data(self) -> Dict:
        """Load calendar data."""
        try:
            with open(self.calendar_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.ensure_calendar_file()
            return self.load_calendar_data()
    
    def save_calendar_data(self, data: Dict) -> bool:
        """Save calendar data."""
        try:
            with open(self.calendar_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving calendar data: {e}")
            return False
    
    def get_next_salary_payment_date(self) -> Dict:
        """Get next salary payment date."""
        data = self.load_calendar_data()
        payment_day = data.get("salary_payment_day", 25)
        
        today = date.today()
        current_month_payment = date(today.year, today.month, payment_day)
        
        if today <= current_month_payment:
            next_payment = current_month_payment
        else:
            next_month = today + relativedelta(months=1)
            next_payment = date(next_month.year, next_month.month, payment_day)
        
        days_until = (next_payment - today).days
        
        return {
            "next_payment_date": next_payment.strftime("%Y-%m-%d"),
            "days_until": days_until,
            "payment_day": payment_day,
            "burmese_date": self._format_burmese_date(next_payment)
        }
    
    def set_salary_payment_day(self, day: int) -> Dict:
        """Set salary payment day (1-31)."""
        if not (1 <= day <= 31):
            return {"error": "လစာထုတ်ရက်သည် ၁ မှ ၃၁ ရက်အတွင်း ရှိရမည်"}
        
        data = self.load_calendar_data()
        data["salary_payment_day"] = day
        
        if self.save_calendar_data(data):
            return {
                "success": True,
                "message": f"လစာထုတ်ရက်ကို လတိုင်း {day} ရက်အဖြစ် သတ်မှတ်ပြီးပါပြီ",
                "payment_day": day
            }
        else:
            return {"error": "လစာထုတ်ရက်သတ်မှတ်ရာတွင် အမှားရှိခဲ့သည်"}
    
    def add_user_event(self, user_id: str, event_date: str, event_type: str, 
                      description: str, reminder_time: str = None) -> Dict:
        """Add user event to calendar."""
        try:
            # Validate date format
            event_datetime = datetime.strptime(event_date, "%Y-%m-%d")
            
            data = self.load_calendar_data()
            if user_id not in data["users"]:
                data["users"][user_id] = {"events": []}
            
            event = {
                "id": f"{user_id}_{event_date}_{len(data['users'][user_id]['events'])}",
                "date": event_date,
                "type": event_type,
                "description": description,
                "reminder_time": reminder_time,
                "created_at": datetime.now().isoformat()
            }
            
            data["users"][user_id]["events"].append(event)
            
            if self.save_calendar_data(data):
                return {
                    "success": True,
                    "message": f"ပွဲအစီအစဉ် '{description}' ကို {self._format_burmese_date(event_datetime.date())} တွင် ထည့်ပြီးပါပြီ",
                    "event": event
                }
            else:
                return {"error": "ပွဲအစီအစဉ်ထည့်ရာတွင် အမှားရှိခဲ့သည်"}
                
        except ValueError:
            return {"error": "ရက်စွဲပုံစံမှားနေပါသည်။ YYYY-MM-DD ပုံစံဖြင့် ရေးပါ"}
    
    def get_user_events(self, user_id: str, days: int = 30) -> Dict:
        """Get user events for the next N days."""
        data = self.load_calendar_data()
        
        if user_id not in data["users"]:
            return {"error": "မည်သည့်ပွဲအစီအစဉ်မျှ မရှိသေးပါ"}
        
        user_events = data["users"][user_id]["events"]
        today = date.today()
        end_date = today + timedelta(days=days)
        
        upcoming_events = []
        for event in user_events:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
            if today <= event_date <= end_date:
                days_until = (event_date - today).days
                upcoming_events.append({
                    **event,
                    "days_until": days_until,
                    "burmese_date": self._format_burmese_date(event_date)
                })
        
        # Sort by date
        upcoming_events.sort(key=lambda x: x["date"])
        
        return {
            "events": upcoming_events,
            "total_events": len(upcoming_events),
            "period": f"နောက်ဆုံး {days} ရက်"
        }
    
    def delete_user_event(self, user_id: str, event_id: str) -> Dict:
        """Delete user event."""
        data = self.load_calendar_data()
        
        if user_id not in data["users"]:
            return {"error": "မည်သည့်ပွဲအစီအစဉ်မျှ မရှိသေးပါ"}
        
        user_events = data["users"][user_id]["events"]
        
        # Find and remove event
        for i, event in enumerate(user_events):
            if event["id"] == event_id:
                deleted_event = user_events.pop(i)
                if self.save_calendar_data(data):
                    return {
                        "success": True,
                        "message": f"ပွဲအစီအစဉ် '{deleted_event['description']}' ကို ဖျက်ပြီးပါပြီ"
                    }
                else:
                    return {"error": "ပွဲအစီအစဉ်ဖျက်ရာတွင် အမှားရှိခဲ့သည်"}
        
        return {"error": "ပွဲအစီအစဉ်ရှာမတွေ့ပါ"}
    
    def get_monthly_calendar(self, user_id: str, year: int, month: int) -> Dict:
        """Get monthly calendar view."""
        try:
            data = self.load_calendar_data()
            payment_day = data.get("salary_payment_day", 25)
            
            # Get events for the month
            user_events = []
            if user_id in data["users"]:
                for event in data["users"][user_id]["events"]:
                    event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
                    if event_date.year == year and event_date.month == month:
                        user_events.append({
                            **event,
                            "day": event_date.day,
                            "burmese_date": self._format_burmese_date(event_date)
                        })
            
            # Calculate salary payment date for the month
            try:
                salary_date = date(year, month, payment_day)
                salary_info = {
                    "day": payment_day,
                    "date": salary_date.strftime("%Y-%m-%d"),
                    "burmese_date": self._format_burmese_date(salary_date)
                }
            except ValueError:
                # Handle months with fewer days
                last_day = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year + 1, 1, 1) - timedelta(days=1)
                salary_date = date(year, month, min(payment_day, last_day.day))
                salary_info = {
                    "day": salary_date.day,
                    "date": salary_date.strftime("%Y-%m-%d"),
                    "burmese_date": self._format_burmese_date(salary_date)
                }
            
            return {
                "year": year,
                "month": month,
                "month_name": self._get_burmese_month(month),
                "events": user_events,
                "salary_payment": salary_info,
                "total_events": len(user_events)
            }
            
        except Exception as e:
            return {"error": f"လစွဲပြက္ခဒိန်ရာတွင် အမှားရှိခဲ့သည်: {str(e)}"}
    
    def get_work_schedule_suggestions(self, user_id: str) -> Dict:
        """Get work schedule suggestions based on salary payment dates."""
        try:
            from data_storage import DataStorage
            
            storage = DataStorage()
            user_data = storage.load_user_data(user_id)
            
            if not user_data:
                return {"error": "အလုပ်မှတ်တမ်းမရှိသေးပါ"}
            
            # Calculate average daily salary from user data
            all_calculations = []
            for date_data in user_data.values():
                if isinstance(date_data, list):
                    all_calculations.extend(date_data)
            
            if not all_calculations:
                return {"error": "လတ်တလော အလုပ်မှတ်တမ်းမရှိပါ"}
            
            # Get last 30 calculations
            recent_calculations = all_calculations[-30:]
            avg_daily_salary = sum(calc["total_salary"] for calc in recent_calculations) / len(recent_calculations)
            
            # Get next salary payment date
            payment_info = self.get_next_salary_payment_date()
            days_until_payment = payment_info["days_until"]
            
            # Calculate suggested work schedule
            if days_until_payment > 0:
                # Suggest target for remaining days
                target_monthly_salary = avg_daily_salary * 25  # Assume 25 working days per month
                # Calculate current month total
                current_month = datetime.now().strftime("%Y-%m")
                current_month_total = 0
                for date_str, date_data in user_data.items():
                    if date_str.startswith(current_month) and isinstance(date_data, list):
                        for calc in date_data:
                            current_month_total += calc["total_salary"]
                
                remaining_needed = max(0, target_monthly_salary - current_month_total)
                suggested_daily = remaining_needed / days_until_payment if days_until_payment > 0 else 0
                
                return {
                    "next_payment": payment_info,
                    "avg_daily_salary": avg_daily_salary,
                    "target_monthly": target_monthly_salary,
                    "current_month_total": current_month_total,
                    "remaining_needed": remaining_needed,
                    "suggested_daily": suggested_daily,
                    "days_until_payment": days_until_payment,
                    "suggestion": f"လစာထုတ်ရက်အထိ နေ့စဉ် ¥{suggested_daily:,.0f} ရလိုအပ်ပါသည်"
                }
            else:
                return {
                    "next_payment": payment_info,
                    "message": "ယနေ့သည် လစာထုတ်ရက်ဖြစ်ပါသည်! 🎉"
                }
                
        except Exception as e:
            return {"error": f"အလုပ်အစီအစဉ်အကြံပြုချက်ရာတွင် အမှားရှိခဲ့သည်: {str(e)}"}
    
    def _format_burmese_date(self, date_obj: date) -> str:
        """Format date in Burmese."""
        burmese_months = [
            "ဇန်နဝါရီ", "ဖေဖော်ဝါရီ", "မတ်", "ဧပြီ", "မေ", "ဇွန်",
            "ဇူလိုင်", "ဩဂုတ်", "စက်တင်ဘာ", "အောက်တိုဘာ", "နိုဝင်ဘာ", "ဒီဇင်ဘာ"
        ]
        
        burmese_days = ["တနင်္လာ", "တနင်္ဂနွေ", "ဗုဒ္ဓဟူး", "ကြာသပတေး", "သောကြာ", "စနေ", "တနင်္ဂနွေ"]
        
        day_name = burmese_days[date_obj.weekday()]
        month_name = burmese_months[date_obj.month - 1]
        
        return f"{day_name}၊ {month_name} {date_obj.day}၊ {date_obj.year}"
    
    def _get_burmese_month(self, month: int) -> str:
        """Get Burmese month name."""
        burmese_months = [
            "ဇန်နဝါရီ", "ဖေဖော်ဝါရီ", "မတ်", "ဧပြီ", "မေ", "ဇွန်",
            "ဇူလိုင်", "ဩဂုတ်", "စက်တင်ဘာ", "အောက်တိုဘာ", "နိုဝင်ဘာ", "ဒီဇင်ဘာ"
        ]
        return burmese_months[month - 1]
    
    def get_today_events(self, user_id: str) -> Dict:
        """Get today's events."""
        try:
            data = self.load_calendar_data()
            
            if user_id not in data["users"]:
                return {
                    "events": [], 
                    "total": 0,
                    "date": date.today().strftime("%Y-%m-%d"),
                    "burmese_date": self._format_burmese_date(date.today())
                }
            
            today_str = date.today().strftime("%Y-%m-%d")
            today_events = []
            
            for event in data["users"][user_id]["events"]:
                if event["date"] == today_str:
                    today_events.append({
                        **event,
                        "burmese_date": self._format_burmese_date(date.today())
                    })
            
            return {
                "events": today_events,
                "total": len(today_events),
                "date": today_str,
                "burmese_date": self._format_burmese_date(date.today())
            }
        except Exception as e:
            # Return safe fallback
            return {
                "events": [], 
                "total": 0,
                "date": date.today().strftime("%Y-%m-%d"),
                "burmese_date": "ယနေ့"
            }