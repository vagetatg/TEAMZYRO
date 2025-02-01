import urllib.request
from pymongo import ReturnDocument
import os
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from TEAMZYRO import application, collection, db



async def check_total_characters(update: Update, context: CallbackContext) -> None:
    try:
        total_characters = await collection.count_documents({})
        
        await update.message.reply_text(f"Total number of characters: {total_characters}")
    except Exception as e:
        await update.message.reply_text(f"Error occurred: {e}")

async def check(update: Update, context: CallbackContext) -> None:    
     try:
        args = context.args
        if len(context.args) != 1:
            await update.message.reply_text('Incorrect format. Please use: /check id')
            return
            
        character_id = context.args[0]
         # Get character name from the command arguments
        
        character = await collection.find_one({'id': args[0]}) 
            
        if character:
            # If character found, send the information along with the image URL
            message = f"<b>Character Name:</b> {character['name']}\n" \
                      f"<b>Anime Name:</b> {character['anime']}\n" \
                      f"<b>Rarity:</b> {character['rarity']}\n" \
                      f"<b>ID:</b> {character['id']}\n"

            await context.bot.send_photo(chat_id=update.effective_chat.id,
                                         photo=character['img_url'],
                                         caption=message,
                                         parse_mode='HTML')
        else:
            await update.message.reply_text("Character not found.")
     except Exception as e:
        await update.message.reply_text(f"Error occurred: {e}")



application.add_handler(CommandHandler("total", check_total_characters))

CHECK_HANDLER = CommandHandler('check', check, block=False)
application.add_handler(CHECK_HANDLER)














