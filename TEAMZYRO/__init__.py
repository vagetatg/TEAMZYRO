from SafoneAPI import SafoneAPI

from TEAMZYRO.core.bot import Hotty
from TEAMZYRO.core.dir import dirr
from TEAMZYRO.core.git import git
from TEAMZYRO.core.userbot import Userbot
from TEAMZYRO.misc import dbb, heroku
from TEAMZYRO.core.application import main, application
from .logging import LOGGER

dirr()
git()
dbb()
heroku()
main()

app = Hotty()
userbot = Userbot()
api = SafoneAPI()
apl = application

from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

APP = "Raiden_Robot"  # connect music api key "Dont change it"

#-------------------goku------------------×


from motor.motor_asyncio import AsyncIOMotorClient
from telegram.ext import Application
from config import BOT_TOKEN



application = Application.builder().token(BOT_TOKEN).build()

ZYRO = AsyncIOMotorClient(mongo_url)
db = ZYRO['gaming_create']
user_totals_collection = db['gaming_totals']
group_user_totals_collection = db['gaming_group_total']
top_global_groups_collection = db['gaming_global_groups']
pm_users = db['gaming_pm_users']
destination_collection = db['gamimg_user_collection']
destination_char = db['gaming_anime_characters']
#----------------------GOKU-------------×
collection = destination_char
user_collection = destination_collection
