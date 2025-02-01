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
