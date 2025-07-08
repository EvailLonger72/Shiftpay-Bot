#!/usr/bin/env python3
"""Test script to verify all new features work correctly."""

from export_manager import ExportManager
from notifications import NotificationManager
from goal_tracker import GoalTracker
from data_storage import DataStorage
from salary_calculator import SalaryCalculator
from datetime import datetime, timedelta
import json

def test_all_new_features():
    """Test all new features comprehensively."""
    print("🧪 Testing All New Features")
    print("=" * 60)
    
    # Initialize all components
    export_manager = ExportManager()
    notification_manager = NotificationManager()
    goal_tracker = GoalTracker()
    storage = DataStorage()
    calculator = SalaryCalculator()
    
    test_user_id = "test_user_456"
    
    # Create test data
    print("\n📊 Creating test data...")
    test_entries = [
        ("08:30", "17:30"),
        ("09:00", "18:00"),
        ("16:45", "01:25"),
        ("08:00", "16:30"),
        ("09:30", "18:30")
    ]
    
    for i, (start, end) in enumerate(test_entries):
        result = calculator.calculate_salary(start, end)
        if not result.get('error'):
            storage.save_calculation(test_user_id, result)
            print(f"   Added: {start} ~ {end}")
    
    print("\n" + "=" * 60)
    print("🎯 Testing Goal Tracker...")
    
    # Test goal setting
    monthly_salary_goal = goal_tracker.set_monthly_goal(test_user_id, 'salary', 300000)
    print(f"Monthly salary goal: {monthly_salary_goal.get('message', 'Error')}")
    
    monthly_hours_goal = goal_tracker.set_monthly_goal(test_user_id, 'hours', 180)
    print(f"Monthly hours goal: {monthly_hours_goal.get('message', 'Error')}")
    
    weekly_salary_goal = goal_tracker.set_weekly_goal(test_user_id, 'salary', 70000)
    print(f"Weekly salary goal: {weekly_salary_goal.get('message', 'Error')}")
    
    # Test goal progress
    progress = goal_tracker.check_goal_progress(test_user_id, 'monthly')
    if not progress.get('error'):
        print(f"\n📈 Monthly Goal Progress:")
        for goal_type, data in progress.get('progress', {}).items():
            print(f"   {goal_type}: {data['progress_percent']:.1f}% complete")
    
    # Test goal recommendations
    recommendations = goal_tracker.get_goal_recommendations(test_user_id)
    if not recommendations.get('error'):
        print(f"\n💡 Goal Recommendations:")
        for rec in recommendations.get('recommendations', []):
            print(f"   • {rec}")
    
    print("\n" + "=" * 60)
    print("🔔 Testing Notification Manager...")
    
    # Test work reminder
    reminder = notification_manager.set_work_reminder(test_user_id, "08:00", "မနက် ၈ နာရီ အလုပ်ချိန်!")
    print(f"Work reminder: {reminder.get('message', reminder.get('error'))}")
    
    # Test streak info
    streak_info = notification_manager.get_streak_info(test_user_id)
    if not streak_info.get('error'):
        print(f"Work streak: Current {streak_info['current_streak']}, Longest {streak_info['longest_streak']}")
    
    # Test performance alert
    alert_info = notification_manager.generate_work_summary_alert(test_user_id)
    if not alert_info.get('error'):
        print(f"Performance alert: {alert_info.get('message', 'No alerts')}")
    
    # Test missing entries
    missing_info = notification_manager.check_missing_entries(test_user_id, 7)
    if not missing_info.get('error'):
        print(f"Missing entries: {missing_info['total_missing']} days")
    
    print("\n" + "=" * 60)
    print("📤 Testing Export Manager...")
    
    # Test CSV export
    csv_data = export_manager.export_to_csv(test_user_id, 30)
    if csv_data:
        print("✅ CSV export successful")
        print(f"   Data size: {len(csv_data)} characters")
        
        # Save test CSV
        with open(f"test_export_{test_user_id}.csv", 'w', encoding='utf-8') as f:
            f.write(csv_data)
        print("   Test CSV file saved")
    else:
        print("❌ CSV export failed")
    
    # Test JSON export
    json_data = export_manager.export_to_json(test_user_id, 30)
    if json_data:
        print("✅ JSON export successful")
        print(f"   Data size: {len(json_data)} characters")
        
        # Save test JSON
        with open(f"test_export_{test_user_id}.json", 'w', encoding='utf-8') as f:
            f.write(json_data)
        print("   Test JSON file saved")
    else:
        print("❌ JSON export failed")
    
    # Test monthly report
    monthly_report = export_manager.generate_monthly_report(test_user_id, 7, 2025)
    if not monthly_report.get('error'):
        print(f"✅ Monthly report generated for July 2025")
        print(f"   Total days: {monthly_report['total_days']}")
        print(f"   Total salary: ¥{monthly_report['total_salary']:,.0f}")
        print(f"   Total hours: {monthly_report['total_hours']} hours")
    else:
        print(f"❌ Monthly report error: {monthly_report['error']}")
    
    # Test export summary
    export_summary = export_manager.get_export_summary(test_user_id, 30)
    if not export_summary.get('error'):
        print(f"✅ Export summary:")
        print(f"   Records: {export_summary['total_records']}")
        print(f"   Days: {export_summary['total_days']}")
        print(f"   Date range: {export_summary['date_range']['start']} to {export_summary['date_range']['end']}")
    
    print("\n" + "=" * 60)
    print("🧹 Cleaning up test data...")
    
    # Clean up test data
    storage.delete_user_data(test_user_id)
    
    # Clean up test files
    import os
    for filename in [f"test_export_{test_user_id}.csv", f"test_export_{test_user_id}.json"]:
        try:
            os.remove(filename)
            print(f"   Removed {filename}")
        except:
            pass
    
    print("\n" + "=" * 60)
    print("✅ All new features testing completed!")
    print("\nNew Features Summary:")
    print("   🎯 Goal Tracking - Monthly/Weekly salary and hours goals")
    print("   🔔 Notifications - Work reminders and performance alerts")
    print("   📤 Data Export - CSV/JSON export with file download")
    print("   📊 Advanced Analytics - Monthly reports and export summaries")
    print("   🔥 Work Streaks - Track consecutive work days")
    print("   📅 Missing Day Detection - Find gaps in work records")
    print("   💡 Smart Recommendations - Personalized goal suggestions")

if __name__ == "__main__":
    test_all_new_features()