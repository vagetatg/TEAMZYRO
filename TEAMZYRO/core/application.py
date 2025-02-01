
from telegram.ext import Application
import config 

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
BOT_TOKEN = config.BOT_TOKEN

# Main function to run the bot
def main():
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Run the bot
    print("Bot is running... 🚀")
    application.run_polling()

if __name__ == "__main__":
    main()
