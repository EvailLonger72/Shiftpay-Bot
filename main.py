import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from salary_calculator import SalaryCalculator
from burmese_formatter import BurmeseFormatter
from data_storage import DataStorage
from analytics import Analytics
from export_manager import ExportManager
from notifications import NotificationManager
from goal_tracker import GoalTracker
from calendar_manager import CalendarManager

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SalaryTelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.calculator = SalaryCalculator()
        self.formatter = BurmeseFormatter()
        self.storage = DataStorage()
        self.analytics = Analytics()
        self.export_manager = ExportManager()
        self.notification_manager = NotificationManager()
        self.goal_tracker = GoalTracker()
        self.calendar_manager = CalendarManager()
        self.application = Application.builder().token(token).build()

        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_time_input))
        self.application.add_handler(CallbackQueryHandler(self.handle_button_callback))

    def get_main_keyboard(self):
        """Create the main reply keyboard."""
        keyboard = [
            [
                KeyboardButton("📊 ခွဲခြမ်းစိတ်ဖြာမှု"),
                KeyboardButton("📈 ဂရပ်ပြမှု")
            ],
            [
                KeyboardButton("📋 မှတ်တမ်း"),
                KeyboardButton("🎯 ပန်းတိုင်")
            ],
            [
                KeyboardButton("📅 ပြက္ခဒိန်"),
                KeyboardButton("💰 လစာရက်")
            ],
            [
                KeyboardButton("📤 ပို့မှု"),
                KeyboardButton("🔔 သတိပေးချက်")
            ],
            [
                KeyboardButton("🗑️ ဒေတာဖျက်မှု"),
                KeyboardButton("ℹ️ အကူအညီ")
            ]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        welcome_message = """🤖 **လစာတွက်ချက်စက်ရုံ**

ကြိုဆိုပါတယ်! ဒီ bot က သင့်ရဲ့ နေ့စဉ်လုပ်ငန်းချိန်ကို တွက်ချက်ပေးမှာပါ။

📝 **အသုံးပြုနည်း:**
- စချိန် ~ ဆုံးချိန် (ဥပမာ: 08:30 ~ 17:30)
- အချိန်ပဲ ပို့ပေးရင် ရပါတယ်

🕒 **Shift များ:**
- C341 (နေ့ပိုင်း): 08:30 ~ 17:30
- C342 (ညပိုင်း): 16:45 ~ 01:25

💰 **လစာနှုန်း:**
- ပုံမှန်: ¥2,100/နာရီ
- OT: ¥2,100/နာရီ
- ညဖက် OT: ¥2,625/နာရီ

📱 **အောက်မှ ခလုတ်များကို နှိပ်၍ လုပ်ဆောင်နိုင်ပါသည်**
/help ကို နှိပ်ပြီး အသေးစိတ်ကြည့်ရှုပါ။"""

        keyboard = self.get_main_keyboard()
        await update.message.reply_text(welcome_message, parse_mode='Markdown', reply_markup=keyboard)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send help message."""
        help_message = """📚 **အသေးစိတ်လမ်းညွှန်** / **Detailed Guide**

**⏰ အချိန်ပုံစံများ / Time Formats:**
• `08:30 ~ 17:30` (စချိန် ~ ဆုံးချိန်)
• `2025-07-15 08:30 ~ 17:30` (နေ့စွဲအတွက်)

**🚀 မြန်နည်းလမ်းများ / Quick Commands:**
• `C341` = Day Shift (08:30 ~ 17:30)
• `C342` = Night Shift (16:45 ~ 01:25)
• `ပန်းတိုင် 300000` = လစာပန်းတိုင်သတ်မှတ်
• `ချိန်ပန်းတိုင် 180` = အလုပ်ချိန်ပန်းတိုင်သတ်မှတ်
• `CSV ပို့မယ်` = CSV ဖိုင်ပို့မှု
• `JSON ပို့မယ်` = JSON ဖိုင်ပို့မှု
• `အားလုံးဖျက်မယ်` = ဒေတာအားလုံးဖျက်မှု

**📅 ပြက္ခဒိန် / Calendar:**
• `ပွဲ 2025-07-15 အလုပ်ရှုပ်ပွဲ` = ပွဲအစီအစဉ်ထည့်
• `လစာရက် 25` = လစာထုတ်ရက်သတ်မှတ်

**🏭 Shift အချက်အလက်များ:**

**C341 - Day Shift (08:30 ~ 17:30)**
Break များ: 08:30~08:40, 10:40~11:25, 13:05~13:15, 14:35~14:45, 16:10~16:20, 17:20~17:35

**C342 - Night Shift (16:45 ~ 01:25)**  
Break များ: 18:45~18:55, 20:55~21:40, 23:10~23:20, 00:50~01:00, 02:25~02:35, 03:35~03:50

**💰 လစာတွက်ချက်နည်း:**
• 7h35m အထိ = ¥2,100/နာရီ (ပုံမှန်)
• ကျော်လွန်ရင် = ¥2,100/နာရီ (OT)  
• 22:00 နောက်ပိုင်း = ¥2,625/နာရီ (Night OT)

**🌐 Language Options:**
• မြန်မာ (Burmese) - Default
• English - Available"""

        keyboard = self.get_main_keyboard()
        await update.message.reply_text(help_message, parse_mode='Markdown', reply_markup=keyboard)

    async def handle_time_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle time input from user."""
        try:
            # Check if message exists
            if not update.message or not update.message.text:
                return

            user_input = update.message.text.strip()
            user_id = str(update.effective_user.id)

            # Handle keyboard button presses
            if user_input in ["📊 ခွဲခြမ်းစိတ်ဖြာမှု", "📈 ဂရပ်ပြမှု", "📋 မှတ်တမ်း", "🎯 ပန်းတိုင်", 
                             "📅 ပြက္ခဒိန်", "💰 လစာရက်", "📤 ပို့မှု", "🔔 သတိပေးချက်", "🗑️ ဒေတာဖျက်မှု", "ℹ️ အကူအညီ"]:
                await self.handle_keyboard_button(update, context, user_input)
                return

            # Handle calendar and schedule commands
            if user_input.startswith("ပွဲ "):
                await self.handle_calendar_command(update, context, user_input)
                return
            elif user_input.startswith("လစာရက် "):
                await self.handle_salary_date_command(update, context, user_input)
                return

            # Parse time input
            if '~' not in user_input:
                await update.message.reply_text("❌ **အမှားရှိသည်**\n\nဥပမာ: 08:30 ~ 17:30", parse_mode='Markdown')
                return

            start_time_str, end_time_str = user_input.split('~')
            start_time_str = start_time_str.strip()
            end_time_str = end_time_str.strip()

            # Calculate salary
            result = self.calculator.calculate_salary(start_time_str, end_time_str)

            if result['error']:
                await update.message.reply_text(f"❌ **အမှားရှိသည်**\n\n{result['error']}", parse_mode='Markdown')
                return

            # Save calculation data
            calculation_saved = self.storage.save_calculation(user_id, result)

            # Format response in Burmese
            response = self.formatter.format_salary_response(result)

            # Create inline keyboard with expanded features
            keyboard = [
                [
                    InlineKeyboardButton("📊 ခွဲခြမ်းစိတ်ဖြာမှု", callback_data="analysis"),
                    InlineKeyboardButton("📈 ဂရပ်ပြမှု", callback_data="charts")
                ],
                [
                    InlineKeyboardButton("📋 မှတ်တမ်း", callback_data="history"),
                    InlineKeyboardButton("🎯 ပန်းတိုင်", callback_data="goals_menu")
                ],
                [
                    InlineKeyboardButton("📤 ပို့မှု", callback_data="export_menu"),
                    InlineKeyboardButton("🔔 သတိပေးချက်", callback_data="notifications_menu")
                ],
                [
                    InlineKeyboardButton("🗑️ ဒေတာဖျက်မှု", callback_data="delete_menu")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            keyboard = self.get_main_keyboard()
            await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)

        except Exception as e:
            logger.error(f"Error processing time input: {e}")
            if update.message:
                keyboard = self.get_main_keyboard()
                await update.message.reply_text("❌ **စနစ်အမှားရှိသည်**\n\nကျေးဇူးပြု၍ ထပ်မံကြိုးစားပါ။", parse_mode='Markdown', reply_markup=keyboard)

    async def handle_keyboard_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE, button_text: str) -> None:
        """Handle keyboard button presses."""
        user_id = str(update.effective_user.id)
        keyboard = self.get_main_keyboard()

        try:
            if button_text == "📊 ခွဲခြမ်းစိတ်ဖြာမှု":
                # Generate summary statistics
                stats = self.analytics.generate_summary_stats(user_id, 30)

                if stats.get('error'):
                    response = f"❌ **အမှားရှိသည်**\n\n{stats['error']}"
                else:
                    response = f"""📊 **လစာခွဲခြမ်းစိတ်ဖြာမှု (နောက်ဆုံး ၃၀ ရက်)**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 **စုစုပေါင်းအလုပ်လုပ်ရက်:** {stats['total_days']} ရက်

⏰ **စုစုပေါင်းအလုပ်ချိန်:** {stats['total_work_hours']} နာရီ
   🟢 ပုံမှန်နာရီ: {stats['total_regular_hours']} နာရီ
   🔵 OT နာရီ: {stats['total_ot_hours']} နာရီ

💰 **စုစုပေါင်းလစာ:** ¥{stats['total_salary']:,.0f}

📈 **နေ့စဉ်ပျမ်းမျှ:**
   ⏰ အလုပ်ချိန်: {stats['avg_daily_hours']} နာရီ
   💰 လစာ: ¥{stats['avg_daily_salary']:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)

            elif button_text == "📈 ဂရပ်ပြမှု":
                # Generate bar charts
                chart_data = self.analytics.generate_bar_chart_data(user_id, 14)

                if chart_data.get('error'):
                    response = f"❌ **အမှားရှိသည်**\n\n{chart_data['error']}"
                else:
                    # Create hours chart
                    hours_chart = self.analytics.create_text_bar_chart(chart_data['chart_data'], 'hours')
                    salary_chart = self.analytics.create_text_bar_chart(chart_data['chart_data'], 'salary')

                    response = f"""📈 **နောက်ဆုံး ၁၄ ရက် ဂရပ်**

{hours_chart}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{salary_chart}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)

            elif button_text == "📋 မှတ်တမ်း":
                # Show recent history
                history_data = self.analytics.get_recent_history(user_id, 7)

                if history_data.get('error'):
                    response = f"❌ **အမှားရှိသည်**\n\n{history_data['error']}"
                else:
                    response = "📋 **နောက်ဆုံး ၇ ရက် မှတ်တမ်း**\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

                    for day in history_data['history']:
                        response += f"📅 **{day['date']}**\n"
                        response += f"⏰ {day['hours']}နာရီ (OT: {day['ot_hours']}နာရီ)\n"
                        response += f"💰 ¥{day['salary']:,.0f}\n"
                        response += f"🕒 {day['shifts']}\n\n"

                    response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

                await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)

            elif button_text == "🎯 ပန်းတိုင်":
                # Show goal progress
                progress = self.goal_tracker.check_goal_progress(user_id, 'monthly')

                if progress.get('error'):
                    response = f"""🎯 **ပန်းတိုင်စီမံခန့်ခွဲမှု**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ **အမှားရှိသည်:** {progress['error']}

💡 **အကြံပြုချက်:**
လစဉ်လစာပန်းတိုင် သတ်မှတ်ရန် စာတိုပေးပို့ပါ:
`ပန်းတိုင် 300000` (လစာအတွက်)
`ချိန်ပန်းတိုင် 180` (အလုပ်ချိန်အတွက်)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
                else:
                    response = f"""🎯 **လစဉ်ပန်းတိုင်တိုးတက်မှု**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 **လ:** {progress['month']}
📊 **အလုပ်လုပ်ရက်:** {progress['days_worked']} ရက်

"""

                    for goal_type, goal_data in progress.get('progress', {}).items():
                        if goal_type == 'salary':
                            response += f"""💰 **လစာပန်းတိုင်:**
   🎯 ပန်းတိုင်: ¥{goal_data['target']:,.0f}
   💵 လက်ရှိ: ¥{goal_data['current']:,.0f}
   📈 တိုးတက်မှု: {goal_data['progress_percent']:.1f}%
   🔄 ကျန်: ¥{goal_data['remaining']:,.0f}

"""
                        elif goal_type == 'hours':
                            response += f"""⏰ **အလုပ်ချိန်ပန်းတိုင်:**
   🎯 ပန်းတိုင်: {goal_data['target']} နာရီ
   ⏱️ လက်ရှိ: {goal_data['current']:.1f} နာရီ
   📈 တိုးတက်မှု: {goal_data['progress_percent']:.1f}%
   🔄 ကျန်: {goal_data['remaining']:.1f} နာရီ

"""

                    response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

                await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)

            elif button_text == "📤 ပို့မှု":
                # Show export options
                export_summary = self.export_manager.get_export_summary(user_id, 30)

                if export_summary.get('error'):
                    response = f"""📤 **ဒေတာပို့မှုမီနူး**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ **အမှားရှိသည်:** {export_summary['error']}

💡 **အကြံပြုချက်:**
ပထမဆုံး အလုပ်ချိန်မှတ်သားပြီးမှ ပို့မှုလုပ်ပါ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
                else:
                    response = f"""📤 **ဒေတာပို့မှုမီနူး**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **ပို့နိုင်သောဒေတာ:**
- မှတ်တမ်းအရေအတွက်: {export_summary['total_records']}
- ရက်သတ္တပတ်အရေအတွက်: {export_summary['total_days']}
- ကာလ: {export_summary['date_range']['start']} မှ {export_summary['date_range']['end']}

💡 **ပို့မှုလုပ်ရန်:**
`CSV ပို့မယ်` သို့မဟုတ် `JSON ပို့မယ်` ရေးပေးပါ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)

            elif button_text == "🔔 သတိပေးချက်":
                # Show notifications and streak info
                streak_info = self.notification_manager.get_streak_info(user_id)
                alert_info = self.notification_manager.generate_work_summary_alert(user_id)

                response = f"""🔔 **သတိပေးချက်မီနူး**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 **အလုပ်ဆက်တိုက်ရက်ရေ:**
- လက်ရှိ: {streak_info.get('current_streak', 0)} ရက်
- အမြင့်ဆုံး: {streak_info.get('longest_streak', 0)} ရက်

⚠️ **စွမ်းအားအခြေအနေ:**"""

                if alert_info.get('alert'):
                    response += f"\n{alert_info['message']}"
                else:
                    response += f"\n✅ {alert_info.get('message', 'ကောင်းမွန်နေပါသည်')}"

                response += f"""

💡 **သတိပေးချက်သတ်မှတ်ရန်:**
`သတိပေး 08:00` ရေးပြီး နေ့စဉ်သတိပေးချက်ခံရန်

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)

            elif button_text == "🗑️ ဒေတာဖျက်မှု":
                response = """🗑️ **ဒေတာဖျက်မှုမီနူး**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **သတိပေးချက်:** ဖျက်ပြီးသည်များကို ပြန်လည်ရယူ၍မရပါ

💡 **ဖျက်ရန်:**
`အားလုံးဖျက်မယ်` ရေးပြီးပေးပါ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)

            elif button_text == "📅 ပြက္ခဒိန်":
                # Show calendar and upcoming events
                events = self.calendar_manager.get_user_events(user_id, 30)
                today_events = self.calendar_manager.get_today_events(user_id)

                if events.get('error'):
                    response = f"""📅 **ပြက္ခဒိန်မီနူး**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **ယနေ့ ({today_events['burmese_date']}):** {today_events['total']} ပွဲအစီအစဉ်

📊 **နောက်လာမည့်ပွဲများ:** {events.get('error', 'မရှိပါ')}

💡 **ပွဲအစီအစဉ်ထည့်ရန်:**
`ပွဲ 2025-07-15 အလုပ်ရှုပ်ပွဲ` ပုံစံဖြင့် ရေးပါ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
                else:
                    response = f"""📅 **ပြက္ခဒိန်မီနူး**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **ယနေ့ ({today_events['burmese_date']}):** {today_events['total']} ပွဲအစီအစဉ်

📊 **နောက်လာမည့်ပွဲများ ({events['period']}):**
"""

                    if events['events']:
                        for event in events['events'][:10]:  # Show first 10 events
                            days_text = "ယနေ့" if event['days_until'] == 0 else f"{event['days_until']} ရက်နောက်"
                            response += f"• {event['burmese_date']} ({days_text})\n  📝 {event['description']}\n\n"
                    else:
                        response += "မရှိပါ\n\n"

                    response += f"""💡 **ပွဲအစီအစဉ်ထည့်ရန်:**
`ပွဲ 2025-07-15 အလုပ်ရှုပ်ပွဲ` ပုံစံဖြင့် ရေးပါ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)

            elif button_text == "💰 လစာရက်":
                # Show salary payment information
                payment_info = self.calendar_manager.get_next_salary_payment_date()
                schedule_suggestions = self.calendar_manager.get_work_schedule_suggestions(user_id)

                response = f"""💰 **လစာထုတ်ရက်အချက်အလက်**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 **နောက်လာမည့်လစာရက်:** {payment_info['burmese_date']}
🗓️ **ကျန်ရက်:** {payment_info['days_until']} ရက်
📊 **လစာထုတ်ရက်:** လတိုင်း {payment_info['payment_day']} ရက်

"""

                if schedule_suggestions.get('error'):
                    response += f"📈 **အလုပ်အကြံပြုချက်:** {schedule_suggestions['error']}"
                else:
                    if schedule_suggestions.get('suggestion'):
                        response += f"""📈 **အလုပ်အကြံပြုချက်:**
💵 လက်ရှိလစာ: ¥{schedule_suggestions['current_month_total']:,.0f}
🎯 ပန်းတိုင်: ¥{schedule_suggestions['target_monthly']:,.0f}
📊 {schedule_suggestions['suggestion']}"""
                    else:
                        response += f"🎉 {schedule_suggestions.get('message', 'လစာရက်ရောက်ပြီ!')}"

                response += f"""

💡 **လစာရက်ပြောင်းရန်:**
`လစာရက် 30` ရေးပြီး ၃၀ ရက်အဖြစ် ပြောင်းပါ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)

            elif button_text == "ℹ️ အကူအညီ":
                await self.help(update, context)

        except Exception as e:
            logger.error(f"Error handling keyboard button: {e}")
            response = "❌ **စနစ်အမှားရှိသည်**\n\nကျေးဇူးပြု၍ ထပ်မံကြိုးစားပါသည်။"
            await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)

    async def handle_button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button callbacks for analysis features."""
        query = update.callback_query
        await query.answer()

        user_id = str(update.effective_user.id)
        callback_data = query.data

        try:
            if callback_data == "analysis":
                # Generate summary statistics
                stats = self.analytics.generate_summary_stats(user_id, 30)

                if stats.get('error'):
                    response = f"❌ **အမှားရှိသည်**\n\n{stats['error']}"
                else:
                    response = f"""📊 **လစာခွဲခြမ်းစိတ်ဖြာမှု (နောက်ဆုံး ၃၀ ရက်)**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 **စုစုပေါင်းအလုပ်လုပ်ရက်:** {stats['total_days']} ရက်

⏰ **စုစုပေါင်းအလုပ်ချိန်:** {stats['total_work_hours']} နာရီ
   🟢 ပုံမှန်နာရီ: {stats['total_regular_hours']} နာရီ
   🔵 OT နာရီ: {stats['total_ot_hours']} နာရီ

💰 **စုစုပေါင်းလစာ:** ¥{stats['total_salary']:,.0f}

📈 **နေ့စဉ်ပျမ်းမျှ:**
   ⏰ အလုပ်ချိန်: {stats['avg_daily_hours']} နာရီ
   💰 လစာ: ¥{stats['avg_daily_salary']:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "charts":
                # Generate bar charts
                chart_data = self.analytics.generate_bar_chart_data(user_id, 14)

                if chart_data.get('error'):
                    response = f"❌ **အမှားရှိသည်**\n\n{chart_data['error']}"
                else:
                    # Create hours chart
                    hours_chart = self.analytics.create_text_bar_chart(chart_data['chart_data'], 'hours')
                    salary_chart = self.analytics.create_text_bar_chart(chart_data['chart_data'], 'salary')

                    response = f"""📈 **နောက်ဆုံး ၁၄ ရက် ဂရပ်**

{hours_chart}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{salary_chart}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "history":
                # Show recent history
                history_data = self.analytics.get_recent_history(user_id, 7)

                if history_data.get('error'):
                    response = f"❌ **အမှားရှိသည်**\n\n{history_data['error']}"
                else:
                    response = "📋 **နောက်ဆုံး ၇ ရက် မှတ်တမ်း**\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

                    for day in history_data['history']:
                        response += f"📅 **{day['date']}**\n"
                        response += f"⏰ {day['hours']}နာရီ (OT: {day['ot_hours']}နာရီ)\n"
                        response += f"💰 ¥{day['salary']:,.0f}\n"
                        response += f"🕒 {day['shifts']}\n\n"

                    response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

                await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "delete_menu":
                # Show delete options
                keyboard = [
                    [InlineKeyboardButton("🗑️ အားလုံးဖျက်မည်", callback_data="delete_all")],
                    [InlineKeyboardButton("🔙 ပြန်သွားမည်", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                response = """🗑️ **ဒေတာဖျက်မှုမီနူး**

⚠️ **သတိပေးချက်:** ဖျက်ပြီးသည်များကို ပြန်လည်ရယူ၍မရပါ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

မည်သည့်အရာကို ဖျက်လိုပါသလဲ?"""

                await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)

            elif callback_data == "delete_all":
                # Delete all user data
                success = self.storage.delete_user_data(user_id)

                if success:
                    response = "✅ **ဖျက်မှုအောင်မြင်သည်**\n\nသင့်ဒေတာအားလုံး ဖျက်ပြီးပါပြီ။"
                else:
                    response = "❌ **ဖျက်မှုမအောင်မြင်**\n\nကျေးဇူးပြု၍ ထပ်မံကြိုးစားပါ။"

                await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "goals_menu":
                # Show goals menu
                keyboard = [
                    [
                        InlineKeyboardButton("🎯 ပန်းတိုင်သတ်မှတ်", callback_data="set_goals"),
                        InlineKeyboardButton("📊 တိုးတက်မှု", callback_data="goal_progress")
                    ],
                    [
                        InlineKeyboardButton("🏆 အောင်မြင်မှု", callback_data="achievements"),
                        InlineKeyboardButton("💡 အကြံပြုချက်", callback_data="goal_recommendations")
                    ],
                    [InlineKeyboardButton("🔙 ပြန်သွားမည်", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                response = """🎯 **ပန်းတိုင်စီမံခန့်ခွဲမှု**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

လစာနှင့်အလုပ်ချိန်ပန်းတိုင်များ သတ်မှတ်ပြီး တိုးတက်မှုကို ခြေရာခံပါ။

မည်သည့်ရွေးချယ်မှုကို လုပ်လိုပါသလဲ?"""

                await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)

            elif callback_data == "export_menu":
                # Show export menu
                keyboard = [
                    [
                        InlineKeyboardButton("📊 CSV ပို့မှု", callback_data="export_csv"),
                        InlineKeyboardButton("📄 JSON ပို့မှု", callback_data="export_json")
                    ],
                    [
                        InlineKeyboardButton("📅 လစဉ်အစီရင်ခံစာ", callback_data="monthly_report"),
                        InlineKeyboardButton("ℹ️ ပို့မှုအချက်အလက်", callback_data="export_info")
                    ],
                    [InlineKeyboardButton("🔙 ပြန်သွားမည်", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                response = """📤 **ဒေတာပို့မှုမီနူး**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

သင့်လစာဒေတာကို CSV သို့မဟုတ် JSON ပုံစံဖြင့် ပို့နိုင်ပါသည်။

မည်သည့်ပုံစံဖြင့် ပို့လိုပါသလဲ?"""

                await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)

            elif callback_data == "notifications_menu":
                # Show notifications menu
                keyboard = [
                    [
                        InlineKeyboardButton("⏰ အလုပ်သတိပေးချက်", callback_data="work_reminder"),
                        InlineKeyboardButton("⚠️ စွမ်းအားသတိပေးချက်", callback_data="performance_alert")
                    ],
                    [
                        InlineKeyboardButton("🔥 အလုပ်ဆက်တိုက်", callback_data="work_streak"),
                        InlineKeyboardButton("📅 လစ်ဟန်ရက်", callback_data="missing_days")
                    ],
                    [InlineKeyboardButton("🔙 ပြန်သွားမည်", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                response = """🔔 **သတိပေးချက်မီနူး**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

အလုပ်ချိန်မှတ်သားရန် သတိပေးချက်များနှင့် စွမ်းအားအခြေအနေ ကြည့်ရှုပါ။

မည်သည့်ရွေးချယ်မှုကို လုပ်လိုပါသလဲ?"""

                await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)

            elif callback_data == "export_csv":
                # Export to CSV
                csv_data = self.export_manager.export_to_csv(user_id, 30)

                if csv_data:
                    # Save to file and send
                    filename = f"salary_data_{user_id}_{datetime.now().strftime('%Y%m%d')}.csv"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(csv_data)

                    response = f"""✅ **CSV ပို့မှုအောင်မြင်သည်**

📊 **ဖိုင်အမည်:** {filename}
📅 **နောက်ဆုံး ၃၀ ရက်** ဒေတာပါဝင်ပါသည်

ဖိုင်ကို သင့်ကွန်ပျူတာတွင် Excel သို့မဟုတ် Google Sheets ဖြင့် ဖွင့်နိုင်ပါသည်။"""

                    await query.edit_message_text(response, parse_mode='Markdown')

                    # Send file
                    with open(filename, 'rb') as f:
                        await context.bot.send_document(
                            chat_id=query.message.chat_id,
                            document=f,
                            filename=filename,
                            caption="📊 လစာဒေတာ CSV ဖိုင်"
                        )
                else:
                    response = "❌ **ပို့မှုမအောင်မြင်**\n\nပို့ရန်ဒေတာ မတွေ့ပါ။"
                    await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "export_json":
                # Export to JSON
                json_data = self.export_manager.export_to_json(user_id, 30)

                if json_data:
                    # Save to file and send
                    filename = f"salary_data_{user_id}_{datetime.now().strftime('%Y%m%d')}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(json_data)

                    response = f"""✅ **JSON ပို့မှုအောင်မြင်သည်**

📄 **ဖိုင်အမည်:** {filename}
📅 **နောက်ဆုံး ၃၀ ရက်** ဒေတာပါဝင်ပါသည်

ဖိုင်ကို programming applications များဖြင့် အသုံးပြုနိုင်ပါသည်။"""

                    await query.edit_message_text(response, parse_mode='Markdown')

                    # Send file
                    with open(filename, 'rb') as f:
                        await context.bot.send_document(
                            chat_id=query.message.chat_id,
                            document=f,
                            filename=filename,
                            caption="📄 လစာဒေတာ JSON ဖိုင်"
                        )
                else:
                    response = "❌ **ပို့မှုမအောင်မြင်**\n\nပို့ရန်ဒေတာ မတွေ့ပါ။"
                    await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "work_streak":
                # Show work streak information
                streak_info = self.notification_manager.get_streak_info(user_id)

                if streak_info.get('error'):
                    response = f"❌ **အမှားရှိသည်**\n\n{streak_info['error']}"
                else:
                    response = f"""🔥 **အလုပ်ဆက်တိုက်ရက်ရေ**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 **လက်ရှိဆက်တိုက်:** {streak_info['current_streak']} ရက်
🏆 **အမြင့်မားဆုံး:** {streak_info['longest_streak']} ရက်
📅 **နောက်ဆုံးအလုပ်:** {streak_info['last_work_date'] or 'မရှိသေးပါ'}

{"🎉 ဆက်လက်ကြိုးစားပါ!" if streak_info['current_streak'] > 0 else "💪 ယနေ့အလုပ်လုပ်ပြီး streak စပါ!"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "performance_alert":
                # Show performance alert
                alert_info = self.notification_manager.generate_work_summary_alert(user_id)

                if alert_info.get('error'):
                    response = f"❌ **အမှားရှိသည်**\n\n{alert_info['error']}"
                elif alert_info.get('alert'):
                    response = f"""{alert_info['message']}

💡 **အကြံပြုချက်များ:**
{chr(10).join(f'• {suggestion}' for suggestion in alert_info.get('suggestions', []))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
                else:
                    response = f"""✅ **{alert_info['message']}**

🎯 သင့်အလုပ်စွမ်းအားမှာ ကောင်းမွန်နေပါသည်!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "goal_progress":
                # Show goal progress
                progress = self.goal_tracker.check_goal_progress(user_id, 'monthly')

                if progress.get('error'):
                    response = f"❌ **အမှားရှိသည်**\n\n{progress['error']}"
                else:
                    response = f"""📊 **လစဉ်ပန်းတိုင်တိုးတက်မှု**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 **လ:** {progress['month']}
📊 **အလုပ်လုပ်ရက်:** {progress['days_worked']} ရက်

"""

                    for goal_type, goal_data in progress.get('progress', {}).items():
                        if goal_type == 'salary':
                            response += f"""💰 **လစာပန်းတိုင်:**
   🎯 ပန်းတိုင်: ¥{goal_data['target']:,.0f}
   💵 လက်ရှိ: ¥{goal_data['current']:,.0f}
   📈 တိုးတက်မှု: {goal_data['progress_percent']:.1f}%
   🔄 ကျန်: ¥{goal_data['remaining']:,.0f}

"""
                        elif goal_type == 'hours':
                            response += f"""⏰ **အလုပ်ချိန်ပန်းတိုင်:**
   🎯 ပန်းတိုင်: {goal_data['target']} နာရီ
   ⏱️ လက်ရှိ: {goal_data['current']:.1f} နာရီ
   📈 တိုးတက်မှု: {goal_data['progress_percent']:.1f}%
   🔄 ကျန်: {goal_data['remaining']:.1f} နာရီ

"""

                    response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

                await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "back_to_main":
                # Go back to main menu
                response = "🏠 **ပင်မစာမျက်နှာ**\n\nအချိန်ပေးပို့ပြီး လစာတွက်ချက်ပါ (ဥပမာ: 08:30 ~ 17:30)"

                await query.edit_message_text(response, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error handling button callback: {e}")
            await query.edit_message_text("❌ **စနစ်အမှားရှိသည်**\n\nကျေးဇူးပြု၍ ထပ်မံကြိုးစားပါ။", parse_mode='Markdown')

    async def handle_calendar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str) -> None:
        """Handle calendar event commands."""
        user_id = str(update.effective_user.id)
        keyboard = self.get_main_keyboard()

        try:
            # Parse command: "ပွဲ 2025-07-15 အလုပ်ရှုပ်ပွဲ"
            parts = user_input.split(' ', 2)
            if len(parts) < 3:
                response = """❌ **ပုံစံမှားနေပါသည်**

💡 **မှန်ကန်သောပုံစံ:**
`ပွဲ 2025-07-15 အလုပ်ရှုပ်ပွဲ`

ဥပမာ: `ပွဲ 2025-07-25 လစာထုတ်ရက်`"""
                await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)
                return

            event_date = parts[1]
            description = parts[2]

            # Validate date format
            try:
                datetime.strptime(event_date, "%Y-%m-%d")
                result = self.calendar_manager.add_user_event(user_id, event_date, "custom", description)

                if result.get('error'):
                    response = f"❌ **အမှားရှိသည်**\n\n{result['error']}"
                else:
                    response = f"✅ **ပွဲအစီအစဉ်ထည့်ပြီးပါပြီ**\n\n{result['message']}"
            except ValueError:
                response = """❌ **ရက်စွဲပုံစံမှားနေပါသည်**

💡 **မှန်ကန်သောပုံစံ:**
`ပွဲ 2025-07-15 အလုပ်ရှုပ်ပွဲ`

ဥပမာ: `ပွဲ 2025-07-25 လစာထုတ်ရက်`"""

            await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)

        except Exception as e:
            logger.error(f"Error handling calendar command: {e}")
            response = "❌ **ပွဲအစီအစဉ်ထည့်ရာတွင် အမှားရှိခဲ့သည်**"
            await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)

    async def handle_salary_date_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str) -> None:
        """Handle salary date commands."""
        keyboard = self.get_main_keyboard()

        try:
            # Parse command: "လစာရက် 25"
            parts = user_input.split(' ')
            if len(parts) < 2:
                response = """❌ **ပုံစံမှားနေပါသည်**

💡 **မှန်ကန်သောပုံစံ:**
`လစာရက် 25`

ဥပမာ: `လစာရက် 30` (လတိုင်း ၃၀ ရက်)"""
                await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)
                return

            try:
                day = int(parts[1])
            except ValueError:
                response = "❌ **ရက်သတ္တပတ်သည် နံပါတ်ဖြစ်ရမည်**\n\nဥပမာ: `လစာရက် 25`"
                await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)
                return

            result = self.calendar_manager.set_salary_payment_day(day)

            if result.get('error'):
                response = f"❌ **အမှားရှိသည်**\n\n{result['error']}"
            else:
                response = f"✅ **လစာရက်သတ်မှတ်ပြီးပါပြီ**\n\n{result['message']}"

            await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)

        except Exception as e:
            logger.error(f"Error handling salary date command: {e}")
            response = "❌ **လစာရက်သတ်မှတ်ရာတွင် အမှားရှိခဲ့သည်**"
            await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)

    def run(self):
        """Run the bot."""
        logger.info("Starting Salary Calculator Telegram Bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    # Get bot token from environment variable
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "7786072573:AAE7v8hnE-tfDntqURH9QnbvM3HdAw-umv8")

    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
        return

    # Create and run bot
    bot = SalaryTelegramBot(bot_token)
    bot.run()

if __name__ == "__main__":
    main()