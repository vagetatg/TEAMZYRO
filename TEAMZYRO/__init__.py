from SafoneAPI import SafoneAPI

from TEAMZYRO.core.bot import Hotty
from TEAMZYRO.core.dir import dirr
from TEAMZYRO.core.git import git
from TEAMZYRO.core.userbot import Userbot
from TEAMZYRO.misc import dbb, heroku

from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = Hotty()
userbot = Userbot()
api = SafoneAPI()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

APP = "Raiden_Robot"  # connect music api key "Dont change it"
