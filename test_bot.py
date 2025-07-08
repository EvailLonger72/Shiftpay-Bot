#!/usr/bin/env python3
"""Test script to verify the bot functionality without running Telegram polling."""

from salary_calculator import SalaryCalculator
from burmese_formatter import BurmeseFormatter
from datetime import datetime

def test_salary_calculation():
    """Test the salary calculation functionality."""
    calculator = SalaryCalculator()
    formatter = BurmeseFormatter()
    
    # Test cases
    test_cases = [
        ("08:30", "17:30", "C341 Day Shift"),
        ("16:45", "01:25", "C342 Night Shift"),
        ("09:00", "18:00", "Extended Day Shift"),
        ("17:00", "02:00", "Extended Night Shift")
    ]
    
    print("🧪 Testing Salary Calculator Bot\n")
    print("=" * 50)
    
    for start_time, end_time, test_name in test_cases:
        print(f"\n📊 {test_name}")
        print(f"Input: {start_time} ~ {end_time}")
        print("-" * 30)
        
        try:
            # Calculate salary
            result = calculator.calculate_salary(start_time, end_time)
            
            if result.get('error'):
                print(f"❌ Error: {result['error']}")
            else:
                # Format response
                response = formatter.format_salary_response(result)
                print(response)
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    test_salary_calculation()