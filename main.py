import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from salary_calculator import SalaryCalculator
from burmese_formatter import BurmeseFormatter
from data_storage import DataStorage
from analytics import Analytics
from export_manager import ExportManager
from notifications import NotificationManager
from goal_tracker import GoalTracker

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
        self.application = Application.builder().token(token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_time_input))
        self.application.add_handler(CallbackQueryHandler(self.handle_button_callback))
    
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

/help ကို နှိပ်ပြီး အသေးစိတ်ကြည့်ရှုပါ။"""
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send help message."""
        help_message = """📚 **အသေးစိတ်လမ်းညွှန်**

**Input Format:**
`08:30 ~ 17:30` (စချိန် ~ ဆုံးချိန်)

**C341 - Day Shift (08:30 ~ 17:30)**
Break များ:
- 08:30~08:40 (10 မိနစ်)
- 10:40~11:25 (45 မိနစ်)
- 13:05~13:15 (10 မိနစ်)
- 14:35~14:45 (10 မိနစ်)
- 16:10~16:20 (10 မိနစ်)
- 17:20~17:35 (15 မိနစ်)

**C342 - Night Shift (16:45 ~ 01:25)**
Break များ:
- 18:45~18:55 (10 မိနစ်)
- 20:55~21:40 (45 မိနစ်)
- 23:10~23:20 (10 မိနစ်)
- 00:50~01:00 (10 မိနစ်)
- 02:25~02:35 (10 မိနစ်)
- 03:35~03:50 (15 မိနစ်)

**လစာတွက်ချက်နည်း:**
- 7h35m အထိ = ပုံမှန်နာရီ
- ကျော်လွန်ရင် = OT
- 22:00 နောက်ပိုင်း = Night OT"""
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def handle_time_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle time input from user."""
        try:
            # Check if message exists
            if not update.message or not update.message.text:
                return
            
            user_input = update.message.text.strip()
            
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
            user_id = str(update.effective_user.id)
            self.storage.save_calculation(user_id, result)
            
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
            
            await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error processing time input: {e}")
            if update.message:
                await update.message.reply_text("❌ **စနစ်အမှားရှိသည်**\n\nကျေးဇူးပြု၍ ထပ်မံကြိုးစားပါ။", parse_mode='Markdown')
    
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
