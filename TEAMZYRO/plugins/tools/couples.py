import os
import random
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telegraph import upload_file
from pymongo import MongoClient

COLLECTION_NAME = "coples"
couples_collection = db[COLLECTION_NAME]

# BOT FILE NAME
from TEAMZYRO import app as app

POLICE = [
    [
        InlineKeyboardButton(
            text="ᴍʏ ᴄᴜᴛᴇ ᴅᴇᴠᴇʟᴏᴘᴇʀ  🥀",
            url=f"https://t.me/PiratesMainchat",
        ),
    ],
]


def get_today_date():
    """Get today's date in DD/MM/YYYY format."""
    now = datetime.now()
    return now.strftime("%d/%m/%Y")


def get_tomorrow_date():
    """Get tomorrow's date in DD/MM/YYYY format."""
    tomorrow = datetime.now() + timedelta(days=1)
    return tomorrow.strftime("%d/%m/%Y")


async def save_couple(chat_id, date, couple_data, image_url):
    """Save the couple data to MongoDB."""
    couples_collection.update_one(
        {"chat_id": chat_id, "date": date},
        {"$set": {"couple_data": couple_data, "image_url": image_url}},
        upsert=True,
    )


async def get_couple(chat_id, date):
    """Retrieve the couple data from MongoDB."""
    return couples_collection.find_one({"chat_id": chat_id, "date": date})


@app.on_message(filters.command("couples"))
async def couples_command(_, message):
    cid = message.chat.id
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs.")

    today = get_today_date()
    tomorrow = get_tomorrow_date()

    try:
        # Check if couples are already generated for today
        existing_couple = await get_couple(cid, today)
        if existing_couple:
            c1_id = existing_couple["couple_data"]["c1_id"]
            c2_id = existing_couple["couple_data"]["c2_id"]
            image_url = existing_couple["image_url"]

            N1 = (await app.get_users(c1_id)).mention
            N2 = (await app.get_users(c2_id)).mention

            TXT = f"""
**ᴛᴏᴅᴀʏ's ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ :

{N1} + {N2} = 💚

ɴᴇxᴛ ᴄᴏᴜᴘʟᴇs ᴡɪʟʟ ʙᴇ sᴇʟᴇᴄᴛᴇᴅ ᴏɴ {tomorrow} !!**
"""
            await message.reply_photo(image_url, caption=TXT, reply_markup=InlineKeyboardMarkup(POLICE))
            return

        # Generate new couples
        msg = await message.reply_text("ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴏᴜᴘʟᴇs ɪᴍᴀɢᴇ...")

        # Get list of users
        list_of_users = []
        async for i in app.get_chat_members(message.chat.id, limit=50):
            if not i.user.is_bot:
                list_of_users.append(i.user.id)

        c1_id = random.choice(list_of_users)
        c2_id = random.choice(list_of_users)
        while c1_id == c2_id:
            c1_id = random.choice(list_of_users)

        photo1 = (await app.get_chat(c1_id)).photo
        photo2 = (await app.get_chat(c2_id)).photo

        N1 = (await app.get_users(c1_id)).mention
        N2 = (await app.get_users(c2_id)).mention

        try:
            p1 = await app.download_media(photo1.big_file_id, file_name="pfp.png")
        except Exception:
            p1 = "TEAMZYRO/assets/upic.png"
        try:
            p2 = await app.download_media(photo2.big_file_id, file_name="pfp1.png")
        except Exception:
            p2 = "TEAMZYRO/assets/upic.png"

        img1 = Image.open(f"{p1}")
        img2 = Image.open(f"{p2}")

        img = Image.open("TEAMZYRO/assets/cppicbranded.jpg")

        img1 = img1.resize((437, 437))
        img2 = img2.resize((437, 437))

        mask = Image.new("L", img1.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + img1.size, fill=255)

        mask1 = Image.new("L", img2.size, 0)
        draw = ImageDraw.Draw(mask1)
        draw.ellipse((0, 0) + img2.size, fill=255)

        img1.putalpha(mask)
        img2.putalpha(mask1)

        draw = ImageDraw.Draw(img)

        img.paste(img1, (116, 160), img1)
        img.paste(img2, (789, 160), img2)

        img.save(f"test_{cid}.png")

        TXT = f"""
**ᴛᴏᴅᴀʏ's ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ :

{N1} + {N2} = 💚

ɴᴇxᴛ ᴄᴏᴜᴘʟᴇs ᴡɪʟʟ ʙᴇ sᴇʟᴇᴄᴛᴇᴅ ᴏɴ {tomorrow} !!**
"""

        await message.reply_photo(
            f"test_{cid}.png",
            caption=TXT,
            reply_markup=InlineKeyboardMarkup(POLICE),
        )
        await msg.delete()

        # Upload image to Telegraph and save couple data
        a = upload_file(f"test_{cid}.png")
        image_url = "https://graph.org/" + a[0]
        couple_data = {"c1_id": c1_id, "c2_id": c2_id}
        await save_couple(cid, today, couple_data, image_url)

    except Exception as e:
        print(str(e))
    finally:
        try:
            os.remove(f"./downloads/pfp1.png")
            os.remove(f"./downloads/pfp2.png")
            os.remove(f"test_{cid}.png")
        except Exception:
            pass


__mod__ = "COUPLES"
__help__ = """
**» /couples** - Get Today's Couples Of The Group In Interactive View
"""
