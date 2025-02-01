import urllib.request
from pymongo import ReturnDocument
import os
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from TEAMZYRO import application
from gridfs import GridFS 
from TEAMZYRO import collection, user_collection, db
from io import BytesIO


import os
import requests
from TEAMZYRO import app as shivuu
from pyrogram import filters
from config import CHARA_CHANNEL_ID, SUDOERS, LOGGER_ID

# Define the wrong format message and rarity map
WRONG_FORMAT_TEXT = """Wrong ❌ format...  eg. /upload reply to photo muzan-kibutsuji Demon-slayer 3

format:- /upload reply character-name anime-name rarity-number

use rarity number accordingly rarity Map

rarity_map = {1: "⚪️ Common", 2: "🟣 Rare", 3: "🟡 Legendary", 4: "🟢 Medium", 5: "💮 Special Edition", 6: "🔮 Limited Edition", 7: "🎐 Celestial", 8: "❄️ Winter", 9: "🎃 Halloween", 10: "💝 Valentine", 11: "💸 Premium Edition"}
"""

# Define the channel ID and rarity map
CHARA_CHANNEL_ID = -1002428503112





# Top-level code
rarity_map = {
    1: "⚪️ Common",
    2: "🟣 Rare",
    3: "🟡 Legendary",
    4: "🟢 Medium",
    5: "💮 Special Edition",
    6: "🔮 Limited Edition",
    7: "🎐 Celestial",
    8: "❄️ Winter",
    9: "🎃 Halloween",
    10: "💝 Valentine",
   11: "💸 Premium Edition"   
}
   
# Function to find the next available ID for a character
async def find_available_id():
    cursor = collection.find().sort('id', 1)
    ids = []
    
    async for doc in cursor:
        if 'id' in doc:
            ids.append(doc['id'])
    
    if ids:
        max_id = max(map(int, ids))
        return str(max_id + 1).zfill(2)
    else:
        return '01'  # If no IDs are found, start with '01'

# Function to upload file to Catbox
def upload_to_catbox(file_path):
    url = "https://catbox.moe/user/api.php"
    with open(file_path, "rb") as file:
        response = requests.post(
            url,
            data={"reqtype": "fileupload"},
            files={"fileToUpload": file}
        )
        if response.status_code == 200 and response.text.startswith("https"):
            return response.text
        else:
            raise Exception(f"Error uploading to Catbox: {response.text}")

# Command to upload character information
@shivuu.on_message(filters.command(["cupload"]) & filters.user([7526369190,7078181502]))
async def ul(client, message):
    reply = message.reply_to_message
    if reply and (reply.photo or reply.document):
        args = message.text.split()
        if len(args) != 4:
            await client.send_message(chat_id=message.chat.id, text=WRONG_FORMAT_TEXT)
            return
        
        # Extract character details from the command arguments
        character_name = args[1].replace('-', ' ').title()
        anime = args[2].replace('-', ' ').title()
        rarity = int(args[3])
        
        # Validate rarity value
        if rarity not in rarity_map:
            await message.reply_text("Invalid rarity value. Please use a value between 1 and 13.")
            return
        
        rarity_text = rarity_map[rarity]
        available_id = await find_available_id()

        # Prepare character data
        character = {
            'name': character_name,
            'anime': anime,
            'rarity': rarity_text,
            'id': available_id
        }

        processing_message = await message.reply("<ᴘʀᴏᴄᴇꜱꜱɪɴɢ>....")
        path = await reply.download()
        try:
            # Upload image to Catbox
            catbox_url = upload_to_catbox(path)
            
            # Update character with the image URL
            character['img_url'] = catbox_url
            
            # Send character details to the channel
            await client.send_photo(
                chat_id=CHARA_CHANNEL_ID,
                photo=catbox_url,
                caption=(
                    f"Character Name: {character_name}\n"
                    f"Anime Name: {anime}\n"
                    f"Rarity: {rarity_text}\n"
                    f"ID: {available_id}\n"
                    f"Added by [{message.from_user.first_name}](tg://user?id={message.from_user.id})"
                ),
            )
            
            # Insert character into the database
            await collection.insert_one(character)
            await message.reply_text('CHARACTER ADDED....')
        except Exception as e:
            await message.reply_text(f"Character Upload Unsuccessful. Error: {str(e)}")
        finally:
            os.remove(path)  # Clean up the downloaded file
    else:
        await message.reply_text("Please reply to a photo or document.")

async def check(update: Update, context: CallbackContext) -> None:    
    try:
        args = context.args
        if len(context.args) != 1:
            await update.message.reply_text('Incorrect format. Please use: /check id')
            return
            
        character_id = context.args[0]
        
        character = await collection.find_one({'id': args[0]}) 
            
        if character:
            # If character found, send the information along with the image URL
            message = f"<b>Character Name:</b> {character['name']}\n" \
                      f"<b>Anime Name:</b> {character['anime']}\n" \
                      f"<b>Rarity:</b> {character['rarity']}\n" \
                      f"<b>ID:</b> {character['id']}\n"

            if 'img_url' in character:
                await context.bot.send_photo(chat_id=update.effective_chat.id,
                                             photo=character['img_url'],
                                             caption=message,
                                             parse_mode='HTML')
            elif 'vid_url' in character:
                await context.bot.send_video(chat_id=update.effective_chat.id,
                                             video=character['vid_url'],
                                             caption=message,
                                             parse_mode='HTML')
        else:
             await update.message.reply_text("Character not found.")
    except Exception as e:
        await update.message.reply_text(f"Error occurred: {e}")

async def delete(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('Ask my Owner to use this Command...')
        return

    try:
        args = context.args
        if len(args) != 1:
            await update.message.reply_text('Incorrect format... Please use: /delete ID')
            return

        
        character = await collection.find_one_and_delete({'id': args[0]})
        if character:
            
            await update.message.reply_text('DONE')
        else:
            await update.message.reply_text('Deleted Successfully from db, but character not found In Channel')
    except Exception as e:
        await update.message.reply_text(f'{str(e)}')


async def update(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('You do not have permission to use this command.')
        return

    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text('Incorrect format. Please use: /update id field new_value')
            return

        # Get character by ID
        character = await collection.find_one({'id': args[0]})
        if not character:
            await update.message.reply_text('Character not found.')
            return

        # Check if field is valid
        valid_fields = ['img_url', 'name', 'anime', 'rarity']
        if args[1] not in valid_fields:
            await update.message.reply_text(f'Invalid field. Please use one of the following: {", ".join(valid_fields)}')
            return

        # Update field
        if args[1] in ['name', 'anime']:
            new_value = args[2].replace('-', ' ').title()
        elif args[1] == 'rarity':
            rarity_map = {1: "⚪️ Common", 2: "🟣 Rare", 3: "🟡 Legendary", 4: "🟢 Medium", 5: "💮 Special Edition", 6: "🔮 Limited Edition", 7: "🎐 Celestial", 8: "❄️ Winter",9:"🎃 Halloween", 10: "💝 Valentine", 11: "💸 Premium Edition"}
            try:
                new_value = rarity_map[int(args[2])]
            except KeyError:
                await update.message.reply_text('Invalid rarity. Please use 1, 2, 3, 4, or 5.')
                return
        else:
            new_value = args[2]

        await collection.find_one_and_update({'id': args[0]}, {'$set': {args[1]: new_value}})

        

        await update.message.reply_text('DoNE')
    except Exception as e:
        await update.message.reply_text(f'I guess did not added bot in channel.. or character uploaded Long time ago.. Or character not exits.. orr Wrong id')

        

async def check_total_characters(update: Update, context: CallbackContext) -> None:
    try:
        total_characters = await collection.count_documents({})
        
        await update.message.reply_text(f"Total number of characters: {total_characters}")
    except Exception as e:
        await update.message.reply_text(f"Error occurred: {e}")


async def add_sudo_user(update: Update, context: CallbackContext) -> None:
    if int(update.effective_user.id) == 7078181502:  # Replace OWNER_ID with the ID of the bot owner
        if update.message.reply_to_message and update.message.reply_to_message.from_user:
            new_sudo_user_id = str(update.message.reply_to_message.from_user.id)
            if new_sudo_user_id not in sudo_users:
                sudo_users.append(new_sudo_user_id)
                await update.message.reply_text("User added to sudo users.")
            else:
                await update.message.reply_text("User is already in sudo users.")
        else:
            await update.message.reply_text("Please reply to a message from the user you want to add to sudo users.")
    else:
        await update.message.reply_text("You are not authorized to use this command.")

ADD_SUDO_USER_HANDLER = CommandHandler('add_sudo_user', add_sudo_user, block=False)
application.add_handler(ADD_SUDO_USER_HANDLER)
       
        

ADD_SUDO_USER_HANDLER = CommandHandler('addsudo', add_sudo_user, block=False)
application.add_handler(ADD_SUDO_USER_HANDLER)

        
application.add_handler(CommandHandler("total", check_total_characters))

DELETE_HANDLER = CommandHandler('delete', delete, block=False)
application.add_handler(DELETE_HANDLER)
UPDATE_HANDLER = CommandHandler('update', update, block=False)
application.add_handler(UPDATE_HANDLER)
CHECK_HANDLER = CommandHandler('check', check, block=False)
application.add_handler(CHECK_HANDLER)
