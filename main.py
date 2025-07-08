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
        """Send comprehensive help message."""
        help_message = """📚 **လစာတွက်ချက်ဘော့် - အသေးစိတ်လမ်းညွှန်**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**⏰ အချိန်ပုံစံများ / Time Formats:**

• `08:30 ~ 17:30` (ပုံမှန်ပုံစံ)
• `2025-07-15 08:30 ~ 17:30` (နေ့စွဲပါပုံစံ)
• `C341` = Day Shift (08:30 ~ 17:30)
• `C342` = Night Shift (16:45 ~ 01:25)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🚀 မြန်နည်းလမ်းများ / Quick Commands:**

**🎯 ပန်းတိုင်များ:**
• `ပန်းတိုင် 300000` = လစာပန်းတိုင်သတ်မှတ်
• `ချိန်ပန်းတိုင် 180` = အလုပ်ချိန်ပန်းတိုင်သတ်မှတ်

**📤 Export နှင့် Import:**
• `CSV ပို့မယ်` = CSV ဖိုင်ပို့မှု
• `JSON ပို့မယ်` = JSON ဖိုင်ပို့မှု
• `လစဉ်အစီရင်ခံစာ` = လစဉ်ခွဲခြမ်းစိတ်ဖြာမှု

**🗑️ ဒေတာဖျက်မှု:**
• `အားလုံးဖျက်မယ်` = ဒေတာအားလုံးဖျက်မှု
• `ဟောင်းဒေတာဖျက်မယ်` = ပုံမှန်ရက်ဟောင်းများဖျက်မှု

**📅 ပြက္ခဒိန်နှင့် ပွဲအစီအစဉ်:**
• `ပွဲ 2025-07-15 အလုပ်ရှုပ်ပွဲ` = ပွဲအစီအစဉ်ထည့်သွင်းမှု
• `လစာရက် 25` = လစာထုတ်ရက်သတ်မှတ်မှု

**🔔 သတိပေးချက်များ:**
• `သတိပေး 08:00` = နေ့စဉ်သတိပေးချက်သတ်မှတ်

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🏭 Shift အချက်အလက်များ:**

**C341 - Day Shift (08:30 ~ 17:30)**
• 🕰️ လုပ်ငန်းချိန်: 08:30 မှ 17:30 အထိ
• ⏸️ Break များ: 08:30~08:40, 10:40~11:25, 13:05~13:15, 14:35~14:45, 16:10~16:20, 17:20~17:35
• 💰 လစာနှုန်း: ¥2,100/နာရီ (ပုံမှန်), ¥2,100/နာရီ (OT)

**C342 - Night Shift (16:45 ~ 01:25)**
• 🌙 လုပ်ငန်းချိန်: 16:45 မှ 01:25 အထိ (နောက်တစ်ရက်)
• ⏸️ Break များ: 18:45~18:55, 20:55~21:40, 23:10~23:20, 00:50~01:00, 02:25~02:35, 03:35~03:50
• 💰 လစာနှုန်း: ¥2,100/နာရီ (ပုံမှန်), ¥2,625/နာရီ (Night OT)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**💰 လစာတွက်ချက်နည်း:**

**ပုံမှန်နာရီများ:**
• 7h35m အထိ = ¥2,100/နာရီ
• 7h35m ကျော်လွန်ချက် = OT အဖြစ်သတ်မှတ်

**Overtime (OT) နာရီများ:**
• နေ့ပိုင်း OT = ¥2,100/နာရီ
• ညပိုင်း OT (22:00 နောက်) = ¥2,625/နာရီ

**အပိုထည့်သွင်းချက်များ:**
• Break အချိန်များကို အလိုအလျောက် နုတ်သည်
• နေ့လွန်အလုပ်ကို နေ့သစ်တွင် တွက်ချက်သည်
• အထူးရက်များအတွက် ဘောနပ်စ် (လိုအပ်ရင်)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**📊 အင်္ဂါရပ်များနှင့် လုပ်ဆောင်ချက်များ:**

**ခွဲခြမ်းစိတ်ဖြာမှု:**
• နေ့စဉ်/လစဉ် ခွဲခြမ်းမှု
• Trend Analysis နှင့် ပုံစံများ
• စွမ်းအားကျဆင်းမှု သတိပေးချက်

**ပုံရိပ်ပြမှု:**
• နေ့စဉ် လုပ်ငန်းချိန် Bar Chart
• လစဉ် လစာ Progress Chart
• ပန်းတိုင်နှင့် လက်ရှိအခြေအနေ နှိုင်းယှဉ်မှု

**Export အင်္ဂါရပ်များ:**
• CSV ဖိုင် (Excel အတွက်)
• JSON ဖိုင် (Programming အတွက်)
• PDF အစီရင်ခံစာ (လာမည့်ဗားရှင်းတွင်)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🌐 Language Support:**
• 🇲🇲 မြန်မာ (Burmese) - Primary
• 🇬🇧 English - Available
• 🇯🇵 日本語 - Coming Soon

**📞 ကူညီမှုနှင့် အကြံပြုချက်များ:**
• Bot အတွင်းမှ Help Menu များ
• Quick Start Guide
• FAQ များ (/faq လာမည်)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🔥 အကောင်းဆုံး အလေ့အကျင့်များ:**

1. **နေ့စဉ် မှတ်သားခြင်း:** အလုပ်ပြီးတိုင်း ချက်ချင်း ထည့်ပါ
2. **ပန်းတိုင်သတ်မှတ်ခြင်း:** လစဉ် ပန်းတိုင်များ သတ်မှတ်ပါ
3. **Export လုပ်ခြင်း:** လစဉ် backup လုပ်ထားပါ
4. **Calendar အသုံးပြုခြင်း:** အရေးကြီးရက်များ မှတ်သားပါ
5. **Analytics ကြည့်ရှုခြင်း:** စွမ်းအားကို နေ့စဉ် စစ်ဆေးပါ

💡 **နောက်ထပ်မေးခွန်းများ ရှိပါက keyboard menu များမှတစ်ဆင့် အလွယ်တကူ လုပ်ဆောင်နိုင်ပါသည်။**"""

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
                # Show export options with inline buttons
                export_summary = self.export_manager.get_export_summary(user_id, 30)

                if export_summary.get('error'):
                    response = f"""📤 **ဒေတာပို့မှုမီနူး**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ **အမှားရှိသည်:** {export_summary['error']}

💡 **အကြံပြုချက်:**
ပထမဆုံး အလုပ်ချိန်မှတ်သားပြီးမှ ပို့မှုလုပ်ပါ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
                    
                    await update.message.reply_text(response, parse_mode='Markdown', reply_markup=keyboard)
                else:
                    response = f"""📤 **ဒေတာပို့မှုမီနူး**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **ပို့နိုင်သောဒေတာ:**
- မှတ်တမ်းအရေအတွက်: {export_summary['total_records']}
- ရက်သတ္တပတ်အရေအတွက်: {export_summary['total_days']}
- ကာလ: {export_summary['date_range']['start']} မှ {export_summary['date_range']['end']}

💡 **အောက်မှ option များရွေးချယ်ပါ:**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                    # Create export buttons
                    export_keyboard = [
                        [
                            InlineKeyboardButton("📊 CSV ဖိုင်ပို့မှု", callback_data="export_csv_direct"),
                            InlineKeyboardButton("📄 JSON ဖိုင်ပို့မှု", callback_data="export_json_direct")
                        ],
                        [
                            InlineKeyboardButton("📅 လစဉ်အစီရင်ခံစာ", callback_data="monthly_report"),
                            InlineKeyboardButton("📈 ခွဲခြမ်းစိတ်ဖြာမှုပါ Export", callback_data="export_with_analytics")
                        ]
                    ]
                    export_reply_markup = InlineKeyboardMarkup(export_keyboard)
                    
                    await update.message.reply_text(response, parse_mode='Markdown', reply_markup=export_reply_markup)

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
                # Get user data summary for display
                user_data_summary = self.storage.get_user_data_summary(user_id)

                response = f"""🗑️ **ဒေတာဖျက်မှုဌာန**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **လက်ရှိဒေတာအခြေအနေ:**
• 📋 လုပ်ငန်းမှတ်တမ်း: {user_data_summary.get('total_records', 0)} ရေကောင်
• 🗓️ အလုပ်လုပ်ရက်: {user_data_summary.get('total_days', 0)} ရက်
• 🎯 သတ်မှတ်ပန်းတိုင်: {user_data_summary.get('active_goals', 0)} ခု

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **အရေးကြီးသတိပေးချက်** ⚠️

🔒 **လုံခြုံမှု:** Export လုပ်ပြီးမှ ဖျက်ရန် အကြံပြုပါသည်
🔄 **ရွေးချယ်မှု:** တစ်စိတ်တစ်ပိုင်း သို့မဟုတ် အားလုံးဖျက်နိုင်

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

မည်သည့်ရွေးချယ်မှုကို လုပ်လိုပါသလဲ?"""

                # Create delete options buttons
                delete_keyboard = [
                    [
                        InlineKeyboardButton("🗓️ တစ်လဟောင်းဒေတာ", callback_data="delete_old_month_direct"),
                        InlineKeyboardButton("📅 တစ်ပတ်ဟောင်းဒေတာ", callback_data="delete_old_week_direct")
                    ],
                    [
                        InlineKeyboardButton("🎯 ပန်းတိုင်များဖျက်မယ်", callback_data="delete_goals_direct"),
                        InlineKeyboardButton("📋 မှတ်တမ်းများဖျက်မယ်", callback_data="delete_history_direct")
                    ],
                    [
                        InlineKeyboardButton("📤 Export ပြီးမှ ဖျက်မယ်", callback_data="export_then_delete_direct")
                    ],
                    [
                        InlineKeyboardButton("💥 အားလုံးဖျက်မယ် ⚠️", callback_data="delete_all_confirm_direct")
                    ]
                ]
                delete_reply_markup = InlineKeyboardMarkup(delete_keyboard)
                
                await update.message.reply_text(response, parse_mode='Markdown', reply_markup=delete_reply_markup)

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
                # Show delete options with enhanced styling and more options
                keyboard = [
                    [
                        InlineKeyboardButton("📤 Export ပြီးမှ ဖျက်မယ်", callback_data="export_then_delete"),
                        InlineKeyboardButton("📊 ဒေတာအချက်အလက်", callback_data="data_info")
                    ],
                    [
                        InlineKeyboardButton("🗓️ တစ်လဟောင်းဒေတာ", callback_data="delete_old_month"),
                        InlineKeyboardButton("📅 တစ်ပတ်ဟောင်းဒေတာ", callback_data="delete_old_week")
                    ],
                    [
                        InlineKeyboardButton("🎯 ပန်းတိုင်ဖျက်မယ်", callback_data="delete_goals"),
                        InlineKeyboardButton("📋 မှတ်တမ်းဖျက်မယ်", callback_data="delete_history")
                    ],
                    [
                        InlineKeyboardButton("💥 အားလုံးဖျက်မယ် ⚠️", callback_data="delete_all_confirm")
                    ],
                    [
                        InlineKeyboardButton("🔙 ပြန်သွားမည်", callback_data="back_to_main")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                # Get user data summary for display
                user_data_summary = self.storage.get_user_data_summary(user_id)

                response = f"""🗑️ **ဒေတာဖျက်မှုဌာန**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **လက်ရှိဒေတာအခြေအနေ:**
• 📋 လုပ်ငန်းမှတ်တမ်း: {user_data_summary.get('total_records', 0)} ရေကောင်
• 🗓️ အလုပ်လုပ်ရက်: {user_data_summary.get('total_days', 0)} ရက်
• 🎯 သတ်မှတ်ပန်းတိုင်: {user_data_summary.get('active_goals', 0)} ခု
• 📅 ပွဲအစီအစဉ်: {user_data_summary.get('events', 0)} ခု

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **အရေးကြီးသတိပေးချက်** ⚠️

🔒 **လုံခြုံမှု:** Export လုပ်ပြီးမှ ဖျက်ရန် အကြံပြုပါသည်
🔄 **ရွေးချယ်မှု:** တစ်စိတ်တစ်ပိုင်း သို့မဟုတ် အားလုံးဖျက်နိုင်
⏰ **ချိန်ရွေးချယ်:** ဟောင်းဒေတာများကိုသာ ဖျက်နိုင်

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

မည်သည့်ရွေးချယ်မှုကို လုပ်လိုပါသလဲ?"""

                await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)

            elif callback_data == "export_then_delete":
                # Export data first, then show delete options
                keyboard = [
                    [
                        InlineKeyboardButton("📊 CSV Export ပြီး ဖျက်မယ်", callback_data="csv_then_delete"),
                        InlineKeyboardButton("📄 JSON Export ပြီး ဖျက်မယ်", callback_data="json_then_delete")
                    ],
                    [InlineKeyboardButton("🔙 ပြန်သွားမည်", callback_data="delete_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                response = """📤🗑️ **Export ပြီးမှ ဖျက်မှု**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔒 **လုံခြုံသောနည်းလမ်း:** ဒေတာများကို အရင် backup လုပ်ပြီးမှ ဖျက်ပါ

📋 **လုပ်ဆောင်ချက်များ:**
1. လက်ရှိဒေတာများကို Export လုပ်မည်
2. ဖိုင်ကို သင့်ထံ ပို့မည်
3. အတည်ပြုပြီးမှ ဒေတာဖျက်မည်

🎯 **အကြံပြုချက်:** CSV ဖိုင်သည် Excel တွင် ဖွင့်ရလွယ်ပါသည်

မည်သည့်ပုံစံဖြင့် Export လုပ်လိုပါသလဲ?"""

                await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)

            elif callback_data == "data_info":
                # Show detailed data information
                user_data_summary = self.storage.get_user_data_summary(user_id)
                keyboard = [
                    [InlineKeyboardButton("🔙 ပြန်သွားမည်", callback_data="delete_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                response = f"""📊 **ဒေတာအသေးစိတ်အချက်အလက်**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **လုပ်ငန်းမှတ်တမ်း:**
• စုစုပေါင်း: {user_data_summary.get('total_records', 0)} ရေကောင်
• ပထမဆုံးမှတ်တမ်း: {user_data_summary.get('first_record', 'မရှိ')}
• နောက်ဆုံးမှတ်တမ်း: {user_data_summary.get('last_record', 'မရှိ')}

🗓️ **ကာလအချက်အလက်:**
• အလုပ်လုပ်ရက်: {user_data_summary.get('total_days', 0)} ရက်
• လစဉ်ပျမ်းမျှ: {user_data_summary.get('monthly_avg_days', 0)} ရက်

🎯 **ပန်းတိုင်များ:**
• လက်ရှိလုပ်ဆောင်နေသော: {user_data_summary.get('active_goals', 0)} ခု
• ပြီးမြောက်သော: {user_data_summary.get('completed_goals', 0)} ခု

📅 **ပွဲအစီအစဉ်များ:**
• လက်ရှိပွဲများ: {user_data_summary.get('events', 0)} ခု

💾 **ခန့်မှန်းဖိုင်အရွယ်အစား:**
• CSV: ~{user_data_summary.get('estimated_csv_size', '1KB')}
• JSON: ~{user_data_summary.get('estimated_json_size', '2KB')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)

            elif callback_data == "delete_old_month":
                # Delete data older than 1 month
                success = self.storage.delete_old_data(user_id, 30)
                keyboard = [
                    [InlineKeyboardButton("🔙 ပြန်သွားမည်", callback_data="delete_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                if success:
                    response = """🗓️ **တစ်လဟောင်းဒေတာ ဖျက်ပြီးပါပြီ**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **အောင်မြင်မှု:** ၃၀ ရက်ထက်ပိုဟောင်းသော ဒေတာများ ဖျက်ပြီး
🔄 **ရလဒ်:** လက်ရှိလ ဒေတာများ ကျန်ရှိနေပါသည်
💾 **နေရာ:** စတိုရေ့ချ် နေရာလွတ်ရရှိပါပြီ

🎯 **အကြံပြုချက်:** နောက်လ Export လုပ်ပြီးမှ ဖျက်ပါ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
                else:
                    response = """❌ **ဖျက်မှုမအောင်မြင်**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 **အမှား:** ဟောင်းဒေတာဖျက်ရာတွင် ပြဿနာရှိခဲ့သည်
💡 **ဖြေရှင်းနည်း:** ထပ်မံကြိုးစားပါ သို့မဟုတ် ကူညီမှုရယူပါ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)

            elif callback_data == "delete_old_week":
                # Delete data older than 1 week
                success = self.storage.delete_old_data(user_id, 7)
                keyboard = [
                    [InlineKeyboardButton("🔙 ပြန်သွားမည်", callback_data="delete_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                if success:
                    response = """📅 **တစ်ပတ်ဟောင်းဒေတာ ဖျက်ပြီးပါပြီ**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **အောင်မြင်မှု:** ၇ ရက်ထက်ပိုဟောင်းသော ဒေတာများ ဖျက်ပြီး
🔄 **ရလဒ်:** ယခုပတ် ဒေတာများ ကျန်ရှိနေပါသည်
💾 **နေရာ:** စတိုရေ့ချ် နေရာလွတ်ရရှိပါပြီ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
                else:
                    response = """❌ **ဖျက်မှုမအောင်မြင်**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 **အမှား:** ဟောင်းဒေတာဖျက်ရာတွင် ပြဿနာရှိခဲ့သည်
💡 **ဖြေရှင်းနည်း:** ထပ်မံကြိုးစားပါ သို့မဟုတ် ကူညီမှုရယူပါ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)

            elif callback_data == "delete_goals":
                # Delete goals only
                success = self.goal_tracker.delete_all_goals(user_id)
                keyboard = [
                    [InlineKeyboardButton("🔙 ပြန်သွားမည်", callback_data="delete_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                if success:
                    response = """🎯 **ပန်းတိုင်များ ဖျက်ပြီးပါပြီ**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **အောင်မြင်မှု:** သတ်မှတ်ပန်းတိုင်များ အားလုံး ဖျက်ပြီး
🔄 **ရလဒ်:** အလုပ်မှတ်တမ်းများ မပျက်ပါ
🎯 **သတိ:** ပန်းတိုင်အသစ်များ ပြန်သတ်မှတ်နိုင်ပါသည်

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
                else:
                    response = """❌ **ပန်းတိုင်ဖျက်မှု မအောင်မြင်**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 **အမှား:** ပန်းတိုင်ဖျက်ရာတွင် ပြဿနာရှိခဲ့သည်
💡 **ဖြေရှင်းနည်း:** ထပ်မံကြိုးစားပါ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)

            elif callback_data == "delete_history":
                # Delete work history only
                success = self.storage.delete_work_history(user_id)
                keyboard = [
                    [InlineKeyboardButton("🔙 ပြန်သွားမည်", callback_data="delete_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                if success:
                    response = """📋 **အလုပ်မှတ်တမ်း ဖျက်ပြီးပါပြီ**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **အောင်မြင်မှု:** အလုပ်ချိန်မှတ်တမ်းများ အားလုံး ဖျက်ပြီး
🔄 **ရလဒ်:** ပန်းတိုင်နှင့် ပွဲအစီအစဉ်များ မပျက်ပါ
📱 **သတိ:** ယခုမှ အလုပ်ချိန်အသစ် စတင်နိုင်ပါသည်

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
                else:
                    response = """❌ **မှတ်တမ်းဖျက်မှု မအောင်မြင်**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 **အမှား:** မှတ်တမ်းဖျက်ရာတွင် ပြဿနာရှိခဲ့သည်
💡 **ဖြေရှင်းနည်း:** ထပ်မံကြိုးစားပါ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)

            elif callback_data == "delete_all_confirm":
                # Show final confirmation for deleting all data
                keyboard = [
                    [
                        InlineKeyboardButton("💥 ဟုတ်ကဲ့ အားလုံးဖျက်မယ်", callback_data="delete_all_final"),
                        InlineKeyboardButton("❌ မဖျက်တော့ပါ", callback_data="delete_menu")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                response = """💥 **နောက်ဆုံးအတည်ပြုချက်**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **အန္တရာယ်ကြီးမားသော လုပ်ဆောင်ချက်** ⚠️

🔴 **သင် ဖျက်တော့မည့်အရာများ:**
• 📋 အလုပ်မှတ်တမ်းအားလုံး
• 🎯 ပန်းတိုင်များအားလုံး  
• 📅 ပွဲအစီအစဉ်များအားလုံး
• 🔔 သတိပေးချက်များအားလုံး
• 📊 ခွဲခြမ်းစိတ်ဖြာမှုဒေတာများ

🚨 **သတိပေးချက်များ:**
• ဤလုပ်ဆောင်ချက်ကို ပြန်ပြေးမရပါ
• Export လုပ်ထားခြင်း မရှိပါက ဒေတာများ လုံးဝပျောက်သွားမည်
• စနစ်သည် စတင်အခြေအနေသို့ ပြန်သွားမည်

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💭 **နောက်ဆုံးမေးခွန်း:** သေချာပါသလား?"""

                await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)

            elif callback_data == "delete_all_final":
                # Final delete all user data
                success = self.storage.delete_user_data(user_id)

                if success:
                    response = """🗑️ **အားလုံးဖျက်မှု အောင်မြင်သည်**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **ပြီးမြောက်မှု:** သင့်ဒေတာအားလুံး ဖျက်ပြီးပါပြီ
🔄 **စနစ်အခြေအနေ:** စတင်အခြေအနေသို့ ပြန်သွားပါပြီ
📱 **နောက်ထပ်လုပ်ရမည်:** အချိန်ထည့်ပြီး စတင်နိုင်ပါပြီ

🎉 **လက်ရှိအခြေအနေ:** 
• မှတ်တမ်းများ: 0 ရေကောင်
• ပန်းတိုင်များ: 0 ခု
• ပွဲအစီအစဉ်များ: 0 ခု

💪 **စတင်လိုက်ပါ!** အလုပ်ချိန်ပထမဆုံး ထည့်ကြည့်ပါ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
                else:
                    response = """❌ **အားလုံးဖျက်မှု မအောင်မြင်**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 **အမှား:** ဒေတာဖျက်ရာတွင် စနစ်ပြဿနာရှိခဲ့သည်
🔄 **ကြိုးစားချက်:** ထပ်မံကြိုးစားပါ သို့မဟုတ် Bot restart လုပ်ပါ
📞 **ကူညီမှု:** ပြဿနာဆက်ရှိပါက ထောက်ပံ့မှုဖြင့် ဆက်သွယ်ပါ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

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
                # Show export menu with enhanced styling
                keyboard = [
                    [
                        InlineKeyboardButton("📊 CSV ဖိုင်ပို့မှု", callback_data="export_csv"),
                        InlineKeyboardButton("📄 JSON ဖိုင်ပို့မှု", callback_data="export_json")
                    ],
                    [
                        InlineKeyboardButton("📅 လစဉ်အစီရင်ခံစာ", callback_data="monthly_report"),
                        InlineKeyboardButton("ℹ️ ပို့မှုအချက်အလက်", callback_data="export_info")
                    ],
                    [InlineKeyboardButton("🔙 ပြန်သွားမည်", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                response = """📤 **ဒေတာပို့မှုဌာန**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💾 **ပို့မှုပုံစံများ:**

📊 **CSV ဖိုင်:** Excel, Google Sheets တွင် ဖွင့်နိုင်
📄 **JSON ဖိုင်:** Programming, အခြားစနစ်များအတွက်
📈 **လစဉ်အစီရင်ခံစာ:** အသေးစိတ်ခွဲခြမ်းမှု

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **အကြံပြုချက်:** ဒေတာအရံအားအနေဖြင့် လစဉ် export လုပ်ထားပါ

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
                # Export to CSV with enhanced styling
                csv_data = self.export_manager.export_to_csv(user_id, 30)

                if csv_data:
                    # Save to file and send
                    filename = f"salary_data_{user_id}_{datetime.now().strftime('%Y%m%d')}.csv"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(csv_data)

                    response = f"""📊 **CSV ဖိုင်ပို့မှုအောင်မြင်သည်**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **ပြီးမြောက်မှုအခြေအနေ:** အောင်မြင်
📁 **ဖိုင်အမည်:** {filename}
📅 **ဒေတာကာလ:** နောက်ဆုံး ၃၀ ရက်
💾 **ဖိုင်အမျိုးအစား:** CSV (Comma-Separated Values)

📈 **အသုံးပြုနည်း:**
   • Microsoft Excel တွင် ဖွင့်ခြင်း
   • Google Sheets တွင် import လုပ်ခြင်း
   • Numbers (Mac) တွင် ဖွင့်ခြင်း

🎯 **ပါဝင်သောအချက်အလက်များ:**
   • ရက်စွဲ, အချိန်, Shift အမျိုးအစား
   • လုပ်ငန်းချိန်, OT ချိန်, လစာအသေးစိတ်

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                    await query.edit_message_text(response, parse_mode='Markdown')

                    # Send file
                    with open(filename, 'rb') as f:
                        await context.bot.send_document(
                            chat_id=query.message.chat_id,
                            document=f,
                            filename=filename,
                            caption="📊 လစာဒေတာ CSV ဖိုင် - Excel/Sheets တွင် ဖွင့်နိုင်ပါသည်"
                        )
                else:
                    response = """❌ **CSV ပို့မှုမအောင်မြင်**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 **အမှား:** ပို့ရန်ဒေတာ မတွေ့ပါ
💡 **အကြံပြုချက်:** အချိန်မှတ်သားပြီးမှ export လုပ်ပါ
🔄 **ဖြေရှင်းနည်း:** အလုပ်ချိန်ထည့်ပြီး ပြန်လည်ကြိုးစားပါ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
                    await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "export_json":
                # Export to JSON with enhanced styling
                json_data = self.export_manager.export_to_json(user_id, 30)

                if json_data:
                    # Save to file and send
                    filename = f"salary_data_{user_id}_{datetime.now().strftime('%Y%m%d')}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(json_data)

                    response = f"""📄 **JSON ဖိုင်ပို့မှုအောင်မြင်သည်**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **ပြီးမြောက်မှုအခြေအနေ:** အောင်မြင်
📁 **ဖိုင်အမည်:** {filename}
📅 **ဒေတာကာလ:** နောက်ဆုံး ၃၀ ရက်
💾 **ဖိုင်အမျိုးအစား:** JSON (JavaScript Object Notation)

🛠️ **အသုံးပြုနည်း:**
   • Programming applications များတွင်
   • API integration အတွက်
   • Database import အတွက်
   • Data analysis tools များတွင်

🎯 **ပါဝင်သောအချက်အလက်များ:**
   • အသေးစိတ်ဒေတာဖွဲ့စည်းပုံ
   • Metadata နှင့် timestamps
   • Structured format for developers

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                    await query.edit_message_text(response, parse_mode='Markdown')

                    # Send file
                    with open(filename, 'rb') as f:
                        await context.bot.send_document(
                            chat_id=query.message.chat_id,
                            document=f,
                            filename=filename,
                            caption="📄 လစာဒေတာ JSON ဖိုင် - Programming applications အတွက်"
                        )
                else:
                    response = """❌ **JSON ပို့မှုမအောင်မြင်**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 **အမှား:** ပို့ရန်ဒေတာ မတွေ့ပါ
💡 **အကြံပြုချက်:** အချိန်မှတ်သားပြီးမှ export လုပ်ပါ
🔄 **ဖြေရှင်းနည်း:** အလုပ်ချိန်ထည့်ပြီး ပြန်လည်ကြိုးစားပါ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
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

            elif callback_data == "export_csv_direct":
                # Direct CSV export without menu
                csv_data = self.export_manager.export_to_csv(user_id, 30)

                if csv_data:
                    # Save to file and send
                    filename = f"salary_data_{user_id}_{datetime.now().strftime('%Y%m%d')}.csv"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(csv_data)

                    response = f"""📊 **CSV ဖိုင်ပို့မှုအောင်မြင်သည်**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **ပြီးမြောက်မှု:** အောင်မြင်
📁 **ဖိုင်အမည်:** {filename}
📅 **ဒေတာကာလ:** နောက်ဆုံး ၃၀ ရက်
💾 **အမျိုးအစား:** CSV (Excel ဖွင့်နိုင်)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                    await query.edit_message_text(response, parse_mode='Markdown')

                    # Send file
                    with open(filename, 'rb') as f:
                        await context.bot.send_document(
                            chat_id=query.message.chat_id,
                            document=f,
                            filename=filename,
                            caption="📊 လစာဒေတာ CSV ဖိုင် - Excel/Sheets တွင် ဖွင့်နိုင်ပါသည်"
                        )
                    
                    # Clean up file
                    os.remove(filename)
                else:
                    response = """❌ **CSV ပို့မှုမအောင်မြင်**

ဒေတာ မတွေ့ပါ။ အချိန်မှတ်သားပြီးမှ export လုပ်ပါ။"""
                    await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "export_json_direct":
                # Direct JSON export without menu
                json_data = self.export_manager.export_to_json(user_id, 30)

                if json_data:
                    # Save to file and send
                    filename = f"salary_data_{user_id}_{datetime.now().strftime('%Y%m%d')}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(json_data)

                    response = f"""📄 **JSON ဖိုင်ပို့မှုအောင်မြင်သည်**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **ပြီးမြောက်မှု:** အောင်မြင်
📁 **ဖိုင်အမည်:** {filename}
📅 **ဒေတာကာလ:** နောက်ဆုံး ၃၀ ရက်
💾 **အမျိုးအစား:** JSON (Programming)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

                    await query.edit_message_text(response, parse_mode='Markdown')

                    # Send file
                    with open(filename, 'rb') as f:
                        await context.bot.send_document(
                            chat_id=query.message.chat_id,
                            document=f,
                            filename=filename,
                            caption="📄 လစာဒေတာ JSON ဖိုင် - Programming applications အတွက်"
                        )
                    
                    # Clean up file
                    os.remove(filename)
                else:
                    response = """❌ **JSON ပို့မှုမအောင်မြင်**

ဒေတာ မတွေ့ပါ။ အချိန်မှတ်သားပြီးမှ export လုပ်ပါ။"""
                    await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "export_with_analytics":
                # Export with analytics data
                # First create analytics summary
                stats = self.analytics.generate_summary_stats(user_id, 30)
                chart_data = self.analytics.generate_bar_chart_data(user_id, 14)
                
                # Create comprehensive report
                report_content = f"""လစာတွက်ချက်စက်ရုံ - အစီရင်ခံစာ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 ခွဲခြမ်းစိတ်ဖြာမှု (နောက်ဆုံး ၃၀ ရက်):
- စုစုပေါင်းအလုပ်လုပ်ရက်: {stats.get('total_days', 0)} ရက်
- စုစုပေါင်းအလုပ်ချိန်: {stats.get('total_work_hours', 0)} နာရီ
- ပုံမှန်နာရီ: {stats.get('total_regular_hours', 0)} နာရီ
- OT နာရီ: {stats.get('total_ot_hours', 0)} နာရီ
- စုစုပေါင်းလစာ: ¥{stats.get('total_salary', 0):,.0f}
- နေ့စဉ်ပျမ်းမျှအလုပ်ချိန်: {stats.get('avg_daily_hours', 0)} နာရီ
- နေ့စဉ်ပျမ်းမျှလစာ: ¥{stats.get('avg_daily_salary', 0):,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 အလုပ်ချိန်ပုံစံ (နောက်ဆုံး ၁၄ ရက်):"""

                if not chart_data.get('error'):
                    for day_data in chart_data['chart_data']:
                        report_content += f"\n{day_data['date']}: {day_data['hours']}နာရီ (¥{day_data['salary']:,.0f})"

                # Export data with analytics
                csv_data = self.export_manager.export_to_csv(user_id, 30)
                
                if csv_data:
                    filename = f"salary_analytics_report_{user_id}_{datetime.now().strftime('%Y%m%d')}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(report_content)

                    response = """📈 **ခွဲခြမ်းစိတ်ဖြာမှုပါ အစီရင်ခံစာ ပို့မှုအောင်မြင်သည်**

✅ လုံးဝစုံလင်သော ခွဲခြမ်းစိတ်ဖြာမှုပါ အစီရင်ခံစာကို ပို့ပြီးပါပြီ"""

                    await query.edit_message_text(response, parse_mode='Markdown')

                    # Send analytics report
                    with open(filename, 'rb') as f:
                        await context.bot.send_document(
                            chat_id=query.message.chat_id,
                            document=f,
                            filename=filename,
                            caption="📈 လစာခွဲခြမ်းစိတ်ဖြာမှု အစီရင်ခံစာ"
                        )
                    
                    # Clean up file
                    os.remove(filename)
                else:
                    response = "❌ အစီရင်ခံစာ ပြုလုပ်ရန် ဒေတာ မတွေ့ပါ"
                    await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "delete_old_month_direct":
                # Direct delete old month data
                success = self.storage.delete_old_data(user_id, 30)
                
                if success:
                    response = """🗓️ **တစ်လဟောင်းဒေတာ ဖျက်ပြီးပါပြီ**

✅ ၃၀ ရက်ထက်ပိုဟောင်းသော ဒေတာများ ဖျက်ပြီး
🔄 လက်ရှိလ ဒေတာများ ကျန်ရှိနေပါသည်"""
                else:
                    response = "❌ ဟောင်းဒေတာဖျက်ရာတွင် ပြဿနာရှိခဲ့သည်"
                
                await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "delete_old_week_direct":
                # Direct delete old week data
                success = self.storage.delete_old_data(user_id, 7)
                
                if success:
                    response = """📅 **တစ်ပတ်ဟောင်းဒေတာ ဖျက်ပြီးပါပြီ**

✅ ၇ ရက်ထက်ပိုဟောင်းသော ဒေတာများ ဖျက်ပြီး
🔄 ယခုပတ် ဒေတာများ ကျန်ရှိနေပါသည်"""
                else:
                    response = "❌ ဟောင်းဒေတာဖျက်ရာတွင် ပြဿနာရှိခဲ့သည်"
                
                await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "delete_goals_direct":
                # Direct delete goals
                success = self.goal_tracker.delete_all_goals(user_id)
                
                if success:
                    response = """🎯 **ပန်းတိုင်များ ဖျက်ပြီးပါပြီ**

✅ သတ်မှတ်ပန်းတိုင်များ အားလုံး ဖျက်ပြီး
🔄 အလုပ်မှတ်တမ်းများ မပျက်ပါ"""
                else:
                    response = "❌ ပန်းတိုင်ဖျက်ရာတွင် ပြဿနာရှိခဲ့သည်"
                
                await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "delete_history_direct":
                # Direct delete work history
                success = self.storage.delete_work_history(user_id)
                
                if success:
                    response = """📋 **အလုပ်မှတ်တမ်း ဖျက်ပြီးပါပြီ**

✅ အလုပ်ချိန်မှတ်တမ်းများ အားလုံး ဖျက်ပြီး
🔄 ပန်းတိုင်နှင့် ပွဲအစီအစဉ်များ မပျက်ပါ"""
                else:
                    response = "❌ မှတ်တမ်းဖျက်ရာတွင် ပြဿနာရှိခဲ့သည်"
                
                await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "export_then_delete_direct":
                # Show export then delete options
                keyboard = [
                    [
                        InlineKeyboardButton("📊 CSV Export ပြီး ဖျက်မယ်", callback_data="csv_then_delete_final"),
                        InlineKeyboardButton("📄 JSON Export ပြီး ဖျက်မယ်", callback_data="json_then_delete_final")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                response = """📤🗑️ **Export ပြီးမှ ဖျက်မှု**

🔒 လုံခြုံသောနည်းလမ်း: ဒေတာများကို အရင် backup လုပ်ပြီးမှ ဖျက်ပါ

မည်သည့်ပုံစံဖြင့် Export လုပ်လိုပါသလဲ?"""

                await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)

            elif callback_data == "csv_then_delete_final":
                # Export CSV then delete all
                csv_data = self.export_manager.export_to_csv(user_id, 365)  # Get all data
                
                if csv_data:
                    filename = f"backup_before_delete_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(csv_data)
                    
                    # Send backup file first
                    with open(filename, 'rb') as f:
                        await context.bot.send_document(
                            chat_id=query.message.chat_id,
                            document=f,
                            filename=filename,
                            caption="💾 ဒေတာ backup ဖိုင် - ဖျက်ခြင်းမတိုင်မီ သိမ်းထားပါ"
                        )
                    
                    # Now delete all data
                    delete_success = self.storage.delete_user_data(user_id)
                    
                    if delete_success:
                        response = """📊💥 **CSV Export ပြီး အားလုံးဖျက်မှု အောင်မြင်သည်**

✅ ဒေတာများကို CSV backup လုပ်ပြီး အားလုံးဖျက်ပြီးပါပြီ
💾 Backup ဖိုင်ကို သိမ်းထားပါ
🔄 စနစ်သည် စတင်အခြေအနေသို့ ပြန်သွားပါပြီ"""
                    else:
                        response = """❌ Export အောင်မြင်သော်လည်း ဖျက်မှုမအောင်မြင်

💾 သင့်ဒေတာများ backup လုပ်ပြီးပါပြီ"""
                    
                    # Clean up backup file
                    os.remove(filename)
                else:
                    response = "❌ Export လုပ်ရန် ဒေတာ မတွေ့ပါ"
                
                await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "json_then_delete_final":
                # Export JSON then delete all
                json_data = self.export_manager.export_to_json(user_id, 365)  # Get all data
                
                if json_data:
                    filename = f"backup_before_delete_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(json_data)
                    
                    # Send backup file first
                    with open(filename, 'rb') as f:
                        await context.bot.send_document(
                            chat_id=query.message.chat_id,
                            document=f,
                            filename=filename,
                            caption="💾 ဒေတာ backup ဖိုင် - ဖျက်ခြင်းမတိုင်မီ သိမ်းထားပါ"
                        )
                    
                    # Now delete all data
                    delete_success = self.storage.delete_user_data(user_id)
                    
                    if delete_success:
                        response = """📄💥 **JSON Export ပြီး အားလုံးဖျက်မှု အောင်မြင်သည်**

✅ ဒေတာများကို JSON backup လုပ်ပြီး အားလုံးဖျက်ပြီးပါပြီ
💾 Backup ဖိုင်ကို သိမ်းထားပါ
🔄 စနစ်သည် စတင်အခြေအနေသို့ ပြန်သွားပါပြီ"""
                    else:
                        response = """❌ Export အောင်မြင်သော်လည်း ဖျက်မှုမအောင်မြင်

💾 သင့်ဒေတာများ backup လုပ်ပြီးပါပြီ"""
                    
                    # Clean up backup file
                    os.remove(filename)
                else:
                    response = "❌ Export လုပ်ရန် ဒေတာ မတွေ့ပါ"
                
                await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "delete_all_confirm_direct":
                # Show final confirmation for deleting all data
                keyboard = [
                    [
                        InlineKeyboardButton("💥 ဟုတ်ကဲ့ အားလုံးဖျက်မယ်", callback_data="delete_all_final_direct"),
                        InlineKeyboardButton("❌ မဖျက်တော့ပါ", callback_data="cancel_delete")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                response = """💥 **နောက်ဆုံးအတည်ပြုချက်**

⚠️ **အန္တရာယ်ကြီးမားသော လုပ်ဆောင်ချက်** ⚠️

🔴 သင် ဖျက်တော့မည့်အရာများ:
• 📋 အလုပ်မှတ်တမ်းအားလုံး
• 🎯 ပန်းတိုင်များအားလုံး  
• 📅 ပွဲအစီအစဉ်များအားလုံး
• 🔔 သတိပေးချက်များအားလုံး

🚨 ဤလုပ်ဆောင်ချက်ကို ပြန်ပြေးမရပါ

သေချာပါသလား?"""

                await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)

            elif callback_data == "delete_all_final_direct":
                # Final delete all user data
                success = self.storage.delete_user_data(user_id)

                if success:
                    response = """🗑️ **အားလုံးဖျက်မှု အောင်မြင်သည်**

✅ သင့်ဒေတာအားလုံး ဖျက်ပြီးပါပြီ
🔄 စနစ်အခြေအနေ: စတင်အခြေအနေသို့ ပြန်သွားပါပြီ
📱 အချိန်ထည့်ပြီး စတင်နိုင်ပါပြီ

💪 **စတင်လိုက်ပါ!** အလုပ်ချိန်ပထမဆုံး ထည့်ကြည့်ပါ"""
                else:
                    response = """❌ **အားလုံးဖျက်မှု မအောင်မြင်**

🔴 ဒေတာဖျက်ရာတွင် စနစ်ပြဿနာရှိခဲ့သည်
🔄 ထပ်မံကြိုးစားပါ သို့မဟုတ် Bot restart လုပ်ပါ"""

                await query.edit_message_text(response, parse_mode='Markdown')

            elif callback_data == "cancel_delete":
                response = """❌ **ဖျက်မှုကို ပယ်ဖျက်သည်**

✅ သင့်ဒေတာများ လုံခြုံပါသည်
🔄 မည်သည့်အရာမှ ပြောင်းလဲခြင်း မရှိပါ"""

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