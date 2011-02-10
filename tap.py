import os
import shlex
from twisted.internet import reactor
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

def setup():
    for modname in shlex.split(os.environ.get('autoload_modules', 'Admin')):
        bot.enable_plugin_by_name(modname)

    auto_admin = os.environ.get('auto_admin', os.environ['LOGNAME'])
    bot.auth.addPriv(auto_admin, 'admin')

reactor.callWhenRunning(setup)
