from cassbot import BaseBotPlugin
from twisted.application import internet
from twisted.internet import defer, protocol
from twisted.conch import manhole, insults, telnet

class OpenManhole(BaseBotPlugin):
    service_name = 'bot_manhole'

    def getManhole(self, bot):
        try:
            return bot.service.getServiceNamed(self.service_name)
        except KeyError:
            return None

    def makeManhole(self, bot, port):
        env = {'botserv': bot.service}
        hole = internet.TCPServer(port, MagicManholeFactory(env))
        hole.setName(self.service_name)
        hole.setServiceParent(bot.service)
        return hole

    def command_open_manhole(self, bot, user, channel, args):
        if not args:
            return bot.address_msg(user, channel, "usage: open-manhole <port>")
        hole = self.getManhole(bot)
        if hole is not None:
            return bot.address_msg(user, channel, "Manhole is already open.")
        self.makeManhole(bot, int(args[0]))
        bot.address_msg(user, channel, 'Opened.')

    @defer.inlineCallbacks
    def command_close_manhole(self, bot, user, channel, args):
        if args:
            yield bot.address_msg(user, channel, 'usage: close-manhole')
            return
        hole = self.getManhole(bot)
        if hole is None:
            yield bot.address_msg(user, channel, 'Manhole is not open.')
            return
        yield hole.disownServiceParent()
        yield bot.address_msg(user, channel, 'Closed.')

    def command_is_manhole_open(self, bot, user, channel, args):
        if args:
            return bot.address_msg(user, channel, 'usage: is-manhole-open')
        hole = self.getManhole(bot)
        if hole is not None and hole.running:
            return bot.address_msg(user, channel, 'Manhole is open.')
        return bot.address_msg(user, channel, 'Manhole is not open.')

class ReadlineyManhole(manhole.ColoredManhole):
    def connectionMade(self):
        manhole.ColoredManhole.connectionMade(self)
        # support C-a, C-e, C-h with their normal readline/bash-type
        # behaviors
        self.keyHandlers.update({
            '\x01': self.handle_HOME,
            '\x05': self.handle_END,
            '\x08': self.handle_BACKSPACE,
        })

def MagicManholeFactory(namespace):
    f = protocol.ServerFactory()
    f.protocol = lambda: telnet.TelnetTransport(
        telnet.TelnetBootstrapProtocol,
        insults.insults.ServerProtocol,
        ReadlineyManhole,
        namespace
    )
    return f
