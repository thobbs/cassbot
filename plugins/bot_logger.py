from cassbot import BaseBotPlugin
from twisted.python import log

class BotLogger(BaseBotPlugin):
    eterno_blacklist = ['evn']

    def __init__(self, blacklist=()):
        self.log_blacklist = self.eterno_blacklist + list(blacklist)

    def saveState(self):
        return self.log_blacklist

    def loadState(self, state):
        self.log_blacklist = state

    def irclog(self, *a, **kw):
        kw['mtype'] = 'irclog'
        return log.msg(*a, **kw)

    def signedOn(self, bot):
        self.irclog("Signed on as %s." % (bot.nickname,))

    def joined(self, bot, channel):
        self.irclog("Joined %s." % (channel,))

    def left(self, bot, channel):
        self.irclog("Left %s." % (channel,))

    def noticed(self, bot, user, chan, msg):
        self.irclog("NOTICE -!- [%s] <%s> %s" % (chan, user, msg))

    def modeChanged(self, bot, user, chan, being_set, modes, args):
        self.irclog("MODE -!- %s %s modes %r in %r for %r" % (
            user,
            'set' if being_set else 'unset',
            modes,
            chan,
            args
        ))

    def kickedFrom(self, bot, chan, kicker, msg):
        self.irclog('KICKED -!- from %s by %s [%s]' % (chan, kicker, msg))

    def nickChanged(self, bot, nick):
        self.irclog('NICKCHANGE -!- my nick changed to %s' % (nick,))

    def userJoined(self, bot, user, chan):
        self.irclog('%s joined %s' % (user, chan))

    def userLeft(self, bot, user, chan):
        self.irclog('%s left %s' % (user, chan))

    def userQuit(self, bot, user, msg):
        self.irclog('%s quit [%s]' % (user, msg))

    def userKicked(self, bot, kickee, chan, kicker, msg):
        self.irclog('%s was kicked from %s by %s [%s]' % (kickee, chan, kicker, msg))

    def topicUpdated(self, bot, user, chan, newtopic):
        self.irclog('[%s] -!- topic changed by %s to %r' % (chan, user, newtopic))

    def userRenamed(self, bot, oldname, newname):
        self.irclog('RENAME %s is now known as %s' % (oldname, newname))

    def receivedMOTD(self, bot, motd):
        self.irclog('MOTD %s' % (motd,))

    def msg(self, bot, dest, msg, length=None):
        self.irclog('[%s] <%s> %s' % (dest, bot.nickname, msg))

    def action(self, bot, user, chan, data):
        user = user.split('!', 1)[0]
        if user not in self.log_blacklist:
            self.irclog('[%s] * %s %s' % (chan, user, data))

    def privmsg(self, bot, user, channel, msg):
        user = user.split('!', 1)[0]
        if user not in self.log_blacklist:
            self.irclog('[%s] <%s> %s' % (channel, user, msg))
