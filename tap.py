import os
import shlex
from twisted.application import service
from cassbot import CassBotService

nickname = os.environ.get('nickname', 'CassBotJr')
channels = shlex.split(os.environ.get('channels', ''))
server = os.environ.get('server', 'tcp:host=irc.freenode.net:port=6667')
statefile = os.environ.get('statefile', 'cassbot.state.db')

application = service.Application(nickname)
bot = CassBotService(server, nickname=nickname, init_channels=channels,
                     statefile=statefile)
bot.setServiceParent(application)
