#!/usr/bin/env python3
"""Test script to verify the analytics functionality."""

from salary_calculator import SalaryCalculator
from data_storage import DataStorage
from analytics import Analytics
from datetime import datetime, date, timedelta
import json

def test_analytics():
    """Test the analytics functionality."""
    print("🧪 Testing Analytics Features\n")
    print("=" * 50)
    
    # Initialize components
    calculator = SalaryCalculator()
    storage = DataStorage()
    analytics = Analytics()
    
    # Test user ID
    test_user_id = "test_user_123"
    
    # Create some test data for the last few days
    test_data = [
        ("08:30", "17:30", "Day shift"),
        ("16:45", "01:25", "Night shift"),
        ("09:00", "18:00", "Extended day"),
        ("08:00", "17:00", "Early day")
    ]
    
    print("\n📊 Creating test data...")
    
    # Generate test data for last 5 days
    for i, (start, end, description) in enumerate(test_data):
        print(f"Adding {description}: {start} ~ {end}")
        
        # Calculate salary
        result = calculator.calculate_salary(start, end)
        
        if not result.get('error'):
            # Save with backdated timestamp
            test_date = (date.today() - timedelta(days=i)).isoformat()
            
            # Manually create entry
            user_data = storage.load_user_data(test_user_id)
            if test_date not in user_data:
                user_data[test_date] = []
            
            calculation_entry = {
                'timestamp': datetime.now().isoformat(),
                'start_time': start,
                'end_time': end,
                'shift_type': result['shift_type'],
                'total_minutes': result['total_minutes'],
                'break_minutes': result['break_minutes'],
                'paid_minutes': result['paid_minutes'],
                'regular_minutes': result['regular_minutes'],
                'ot_minutes': result['ot_minutes'],
                'night_ot_minutes': result['night_ot_minutes'],
                'total_salary': result['total_salary'],
                'regular_salary': result['regular_salary'],
                'ot_salary': result['ot_salary'],
                'night_ot_salary': result['night_ot_salary']
            }
            
            user_data[test_date].append(calculation_entry)
            storage.save_user_data(test_user_id, user_data)
    
    print("\n" + "=" * 50)
    print("\n📈 Testing Summary Statistics...")
    
    # Test summary statistics
    stats = analytics.generate_summary_stats(test_user_id, 30)
    
    if stats.get('error'):
        print(f"❌ Error: {stats['error']}")
    else:
        print(f"""📊 **လစာခွဲခြမ်းစိတ်ဖြာမှု (နောက်ဆုံး ၃၀ ရက်)**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 **စုစုပေါင်းအလုပ်လုပ်ရက်:** {stats['total_days']} ရက်

⏰ **စုစုပေါင်းအလုပ်ချိန်:** {stats['total_work_hours']} နာရီ
   🟢 ပုံမှန်နာရီ: {stats['total_regular_hours']} နာရီ
   🔵 OT နာရီ: {stats['total_ot_hours']} နာရီ

💰 **စုစုပေါင်းလစာ:** ¥{stats['total_salary']:,.0f}

📈 **နေ့စဉ်ပျမ်းမျှ:**
   ⏰ အလုပ်ချိန်: {stats['avg_daily_hours']} နာရီ
   💰 လစာ: ¥{stats['avg_daily_salary']:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    
    print("\n" + "=" * 50)
    print("\n📈 Testing Bar Charts...")
    
    # Test bar charts
    chart_data = analytics.generate_bar_chart_data(test_user_id, 7)
    
    if chart_data.get('error'):
        print(f"❌ Error: {chart_data['error']}")
    else:
        # Create hours chart
        hours_chart = analytics.create_text_bar_chart(chart_data['chart_data'], 'hours')
        salary_chart = analytics.create_text_bar_chart(chart_data['chart_data'], 'salary')
        
        print(f"""📈 **နောက်ဆုံး ၇ ရက် ဂရပ်**

{hours_chart}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{salary_chart}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    
    print("\n" + "=" * 50)
    print("\n📋 Testing History...")
    
    # Test history
    history_data = analytics.get_recent_history(test_user_id, 7)
    
    if history_data.get('error'):
        print(f"❌ Error: {history_data['error']}")
    else:
        print("📋 **နောက်ဆုံး ၇ ရက် မှတ်တမ်း**\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        for day in history_data['history']:
            print(f"📅 **{day['date']}**")
            print(f"⏰ {day['hours']}နာရီ (OT: {day['ot_hours']}နာရီ)")
            print(f"💰 ¥{day['salary']:,.0f}")
            print(f"🕒 {day['shifts']}\n")
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    print("\n" + "=" * 50)
    print("\n🗑️ Testing Data Deletion...")
    
    # Test deletion
    success = storage.delete_user_data(test_user_id)
    if success:
        print("✅ **ဖျက်မှုအောင်မြင်သည်**\n\nTရိုစ်ဒေတာအားလုံး ဖျက်ပြီးပါပြီ။")
    else:
        print("❌ **ဖျက်မှုမအောင်မြင်**")
    
    print("\n" + "=" * 50)
    print("✅ Analytics testing completed!")

if __name__ == "__main__":
    test_analytics()