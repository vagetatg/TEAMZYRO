from telegram import Update
from itertools import groupby
import math
from html import escape 
import random

from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from TEAMZYRO import collection, user_collection, application
from config import PARTNER


async def give_character_reply(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in PARTNER:
        await update.message.reply_text('Ask My Owner...')
        return

    try:
        # Check if the reply is to a user message
        if not update.message.reply_to_message or not update.message.reply_to_message.from_user:
            await update.message.reply_text('Reply to a user message to give them a character.')
            return

        args = context.args
        if len(args) != 1:
            await update.message.reply_text('Incorrect format. Please use: /give_character_reply character_id')
            return

        character_id = args[0]
        user_id = update.message.reply_to_message.from_user.id

        # Check if the character exists
        character = await collection.find_one({'id': character_id})
        if not character:
            await update.message.reply_text('Character not found.')
            return

        # Update the user's character list with the given character
        await user_collection.update_one(
            {'id': user_id},
            {'$push': {'characters': character}}
        )

        await update.message.reply_text(f'Character "{character["name"]}" has been given to user with ID {user_id}.')
    except Exception as e:
        await update.message.reply_text(f'An error occurred: {str(e)}')



async def search_character(update: Update, context: CallbackContext):
    # Get the name to search for from the command arguments
    name_to_search = " ".join(context.args).strip()
    
    if not name_to_search:
        await update.message.reply_text("Please provide a name to search for.")
        return

    try:
        # Search for characters by name in the collection
        characters_cursor = collection.find({
            "name": {"$regex": f".*{name_to_search}.*", "$options": "i"}
        })

        found_characters = []
        async for character in characters_cursor:
            found_characters.append(character)

        # Debug: print number of characters found
        print(f"Characters found: {len(found_characters)}")

        if not found_characters:
            await update.message.reply_text("No characters found with that name.")
            return

        # Limit the number of characters displayed (e.g., to 10)
        limit = 80
        displayed_characters = found_characters[:limit]

        # Prepare the response message with found characters
        response_message = "<b>Found Characters:</b>\n"
        for character in displayed_characters:
            response_message += (
                f"ID: {character['id']}\n"
                f"Name: {character['name']}\n"
                f"Rarity: {character['rarity']}\n\n"
            )

        # Check if there are more characters
        if len(found_characters) > limit:
            response_message += "Note: More characters found. Please refine your search."

        await update.message.reply_text(response_message, parse_mode='HTML')
    
    except Exception as e:
        await update.message.reply_text("An error occurred while searching for characters.")
        print(f"Error searching for characters: {e}")




async def remove_character(update: Update, context: CallbackContext):
    if str(update.effective_user.id) not in PARTNER:
        await update.message.reply_text('Ask My Owner...')
        return

    try:
        # Check if the command format is correct
        args = context.args
        if len(args) != 2:
            await update.message.reply_text('Incorrect format. Please use: /remove_character user_id character_id')
            return

        user_id = int(args[0])
        character_id = args[1]

        # Check if the user exists
        user = await user_collection.find_one({'id': user_id})
        if not user:
            await update.message.reply_text('User not found.')
            return

        # Check if the character exists in the user's collection
        character_index = None
        for i, character in enumerate(user['characters']):
            if character['id'] == character_id:
                character_index = i
                break

        if character_index is None:
            await update.message.reply_text('Character not found in user collection.')
            return

        # Remove the character from the user's collection
        del user['characters'][character_index]
        await user_collection.update_one({'id': user_id}, {'$set': {'characters': user['characters']}})

        await update.message.reply_text(f'Character with ID {character_id} has been removed from user with ID {user_id}.')
    except Exception as e:
        await update.message.reply_text(f'An error occurred: {str(e)}')



async def wwhi(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) != 1:
            await update.message.reply_text('Incorrect format. Please use: /wwhi character_id')
            return

        character_id = context.args[0]

        # Retrieve all users from the collection
        all_users = await user_collection.find().to_list(None)

        # Filter users who own the specified character and count its occurrences
        owners = [
            (user['username'], user.get('first_name', 'Unknown'), 
             sum(1 for character in user.get('characters', []) if character['id'] == character_id))
            for user in all_users
            if 'username' in user and user['username'] is not None
        ]

        # Filter out users who do not own the character
        owners = [(username, first_name, count) for username, first_name, count in owners if count > 0]

        if owners:
            # Prepare response message
            response = "Users who own character ID {}:\n".format(character_id)
            response += "\n".join(
                f'<a href="https://t.me/{username}"><b>{first_name}</b></a>: {count} ' 
                for username, first_name, count in owners
            )
            response_chunks = []

            # Split response into chunks if necessary
            while len(response) > 4096:
                response_chunks.append(response[:4096])
                response = response[4096:]

            if response:
                response_chunks.append(response)

            # Send each chunk as a separate message
            for chunk in response_chunks:
                await update.message.reply_text(chunk, parse_mode='HTML')
        else:
            await update.message.reply_text(f'No users have the character with ID {character_id}.')

    except Exception as e:
        await update.message.reply_text(f'An error occurred: {str(e)}')
        print(f"Error in wwhi: {e}")

# Adding the command handler for /wwhi
application.add_handler(CommandHandler("wwhi", wwhi))




# transfer py

async def transfer_collection(update: Update, context: CallbackContext) -> None:
    # Check if the command is run by an owner
    if str(update.effective_user.id) not in PARTNER:
        await update.message.reply_text('Ask My Owner...')
        return

    try:
        # Get the user ID and owner ID
        args = context.args
        if len(args) != 2:
            await update.message.reply_text('Incorrect format. Please use: /transfer user_id owner_id')
            return

        user_id = int(args[0])
        owner_id = int(args[1])

        # Check if the user exists
        user = await user_collection.find_one({'id': user_id})
        if not user:
            await update.message.reply_text('User not found.')
            return

        # Check if the owner exists
        owner = await user_collection.find_one({'id': owner_id})
        if not owner:
            await update.message.reply_text('Owner not found.')
            return

        # Get the user's and owner's character collections
        user_characters = user.get('characters', [])
        owner_characters = owner.get('characters', [])

        if user_characters:
            # Transfer characters from user to owner
            await user_collection.update_one(
                {'id': owner_id},
                {'$push': {'characters': {'$each': user_characters}}}
            )

            # Clear the user's character collection after transfer
            await user_collection.update_one(
                {'id': user_id},
                {'$set': {'characters': []}}
            )

            await update.message.reply_text(
                f"Successfully transferred {len(user_characters)} characters from user with ID {user_id} to owner with ID {owner_id}."
            )
        elif owner_characters:
            # If the user has no characters, transfer from owner back to user
            await user_collection.update_one(
                {'id': user_id},
                {'$push': {'characters': {'$each': owner_characters}}}
            )

            # Clear the owner's character collection after transfer
            await user_collection.update_one(
                {'id': owner_id},
                {'$set': {'characters': []}}
            )

            await update.message.reply_text(
                f"Successfully transferred {len(owner_characters)} characters from owner with ID {owner_id} back to user with ID {user_id}."
            )
        else:
            await update.message.reply_text('Neither the user nor the owner have any characters to transfer.')

    except Exception as e:
        await update.message.reply_text(f'An error occurred: {str(e)}')


# Adding the handler for the /transfer command
application.add_handler(CommandHandler("transfer", transfer_collection))


    
 # application.add_handler(CommandHandler("wwhi", wwhi))
application.add_handler(CommandHandler("take", remove_character))

application.add_handler(CommandHandler("sips", search_character))
GIVE_CHARACTER_REPLY_HANDLER = CommandHandler('give', give_character_reply, block=False)
application.add_handler(GIVE_CHARACTER_REPLY_HANDLER)
