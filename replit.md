# Burmese Salary Calculator Telegram Bot

## Overview

This is a Telegram bot that calculates daily salary for factory workers in Myanmar. The bot automatically detects shift types (Day/Night), correctly deducts break times, and calculates wages including overtime and night overtime rates. All responses are formatted in Burmese language for local users.

## System Architecture

### Core Components
- **Telegram Bot Interface**: Handles user interactions and message processing
- **Salary Calculator**: Core business logic for wage calculations
- **Shift Detector**: Identifies shift types and manages break schedules
- **Time Utilities**: Handles time parsing and calculations
- **Burmese Formatter**: Formats responses in Burmese language

### Technology Stack
- **Backend**: Python with python-telegram-bot library
- **Language**: Python 3.x
- **External APIs**: Telegram Bot API
- **No Database**: Stateless design, processes each request independently

## Key Components

### 1. SalaryTelegramBot (main.py)
- **Purpose**: Main bot controller and Telegram API interface
- **Key Features**:
  - Handles /start and /help commands
  - Processes time input messages
  - Integrates calculator and formatter components
- **Architecture Decision**: Uses async/await pattern for Telegram API calls to handle concurrent users efficiently

### 2. SalaryCalculator (salary_calculator.py)
- **Purpose**: Core business logic for salary calculations
- **Key Features**:
  - Calculates total work minutes
  - Handles break deductions
  - Splits hours into regular, overtime, and night overtime
  - Applies correct wage rates (¥2,100 regular, ¥2,625 night OT)
- **Architecture Decision**: Separates calculation logic from presentation for better maintainability

### 3. ShiftDetector (shift_detector.py)
- **Purpose**: Identifies shift types and manages break schedules
- **Key Features**:
  - Detects C341 (Day Shift) and C342 (Night Shift)
  - Manages break time configurations
  - Handles cross-midnight shifts
- **Architecture Decision**: Centralized shift configuration allows easy addition of new shifts

### 4. TimeUtils (time_utils.py)
- **Purpose**: Utility functions for time parsing and calculations
- **Key Features**:
  - Parses HH:MM format input
  - Handles cross-midnight time calculations
  - Calculates overlaps between work and break times
- **Architecture Decision**: Separate utility class promotes code reuse and testability

### 5. BurmeseFormatter (burmese_formatter.py)
- **Purpose**: Formats calculation results into Burmese Telegram messages
- **Key Features**:
  - Formats salary breakdowns in Burmese
  - Creates visual diagrams for work time
  - Handles error message formatting
- **Architecture Decision**: Separate formatter allows easy localization and message customization

## Data Flow

1. **User Input**: User sends time range (e.g., "08:30 ~ 17:30")
2. **Time Parsing**: TimeUtils parses the input into datetime objects
3. **Shift Detection**: ShiftDetector identifies the shift type and break schedule
4. **Salary Calculation**: SalaryCalculator computes wages with proper deductions
5. **Response Formatting**: BurmeseFormatter creates localized response
6. **Message Delivery**: Bot sends formatted message back to user

## External Dependencies

- **python-telegram-bot**: Official Telegram Bot API wrapper
- **datetime**: Python standard library for time handling
- **logging**: Python standard library for error tracking
- **typing**: Python standard library for type hints

## Deployment Strategy

### Environment Setup
- Requires Telegram Bot Token from BotFather
- No database setup required (stateless design)
- Minimal server requirements due to lightweight architecture

### Configuration
- Bot token stored in environment variables
- Shift configurations hardcoded in ShiftDetector class
- Salary rates configured in SalaryCalculator class

### Scaling Considerations
- Stateless design allows horizontal scaling
- Each request processed independently
- No persistent storage requirements

## Changelog
- July 08, 2025. Initial setup
- July 08, 2025. Completed fully functional Telegram bot with salary calculations

## Recent Changes (July 08, 2025)
✓ Implemented complete Telegram bot with Burmese language support
✓ Added comprehensive salary calculation logic with shift detection
✓ Integrated break time deduction system for C341 and C342 shifts
✓ Built overtime and night overtime calculation system
✓ Created visual timeline diagrams for work periods
✓ Successfully deployed bot with token: 7786072573:AAE7v8hnE-tfDntqURH9QnbvM3HdAw-umv8

## Key Features Implemented
- Automatic shift detection (C341 Day/C342 Night)
- Break time overlap calculation and deduction
- Proper overtime splitting (regular/night rates)
- Burmese language formatting for all responses
- Visual work/break timeline diagrams
- Error handling for invalid inputs

## User Preferences

Preferred communication style: Simple, everyday language.