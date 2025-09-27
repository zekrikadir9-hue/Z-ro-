        """Telegram Bot with tasks and points system"""
        import json, configparser, os
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
        from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

        USERS_FILE = "users.json"
        TASKS_FILE = "tasks.json"

        def load_users():
            if not os.path.exists(USERS_FILE):
                return {}
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        def save_users(data):
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        def load_tasks():
            if not os.path.exists(TASKS_FILE):
                return {}
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        def start(update: Update, context: CallbackContext):
            user = update.effective_user
            users = load_users()
            if str(user.id) not in users:
                users[str(user.id)] = {"balance": 0}
                save_users(users)
            keyboard = [
                [InlineKeyboardButton("🎯 المهام", callback_data="tasks")],
                [InlineKeyboardButton("💰 رصيدي", callback_data="balance")],
                [InlineKeyboardButton("📤 طلب السحب", callback_data="withdraw")],
                [InlineKeyboardButton("📞 تواصل معنا", callback_data="contact")]
            ]
            update.message.reply_text(
                "👋 مرحباً بك في بوت المهام!

قم بتنفيذ المهام واجمع النقاط.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        def handle_buttons(update: Update, context: CallbackContext):
            query = update.callback_query
            query.answer()
            user_id = str(query.from_user.id)
            users = load_users()
            tasks = load_tasks()

            if query.data == "tasks":
                text = "📋 قائمة المهام:
"
                keyboard = []
                for tid, task in tasks.items():
                    text += f"- {task['title']} (+{task['reward']} دج)
"
                    keyboard.append([InlineKeyboardButton(task['title'], callback_data=f"task_{tid}")])
                query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

            elif query.data.startswith("task_"):
                tid = query.data.split("_",1)[1]
                task = load_tasks()[tid]
                users[user_id]["balance"] += task["reward"]
                save_users(users)
                query.edit_message_text(f"✅ أنجزت المهمة: {task['title']} 
💰 تم إضافة {task['reward']} دج لرصيدك.")

            elif query.data == "balance":
                balance = users[user_id]["balance"]
                query.edit_message_text(f"💰 رصيدك الحالي: {balance} دج")

            elif query.data == "withdraw":
                balance = users[user_id]["balance"]
                if balance >= 500:
                    query.edit_message_text("📤 تم استلام طلب السحب. سيتم التواصل معك قريباً.")
                    # Admin notification can be added here
                else:
                    query.edit_message_text("⚠️ تحتاج على الأقل 500 دج لطلب السحب.")

            elif query.data == "contact":
                query.edit_message_text("📞 تواصل معنا:
- الإيميل: zakari.kadir914@gmail.com
- التليجرام: @YourTelegramUsername")

        def main():
            config = configparser.ConfigParser()
            config.read('config.ini')
            token = config.get('bot', 'token', fallback=None)
            if not token or token == "YOUR_BOT_TOKEN_HERE":
                raise SystemExit("ضع توكن البوت في ملف config.ini داخل قسم [bot] المفتاح token")

            updater = Updater(token, use_context=True)
            dp = updater.dispatcher

            dp.add_handler(CommandHandler('start', start))
            dp.add_handler(CallbackQueryHandler(handle_buttons))

            print("🤖 Bot is running...")
            updater.start_polling()
            updater.idle()

        if __name__ == '__main__':
            main()
