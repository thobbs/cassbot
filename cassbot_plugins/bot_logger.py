from cassbot import BaseBotPlugin, natural_list
from twisted.internet import defer
from twisted.python import log

class BotLogger(BaseBotPlugin):
    eterno_blacklist = {'#cassandra': ('evn',), '#cassandra-dev': ('evn',)}

    def __init__(self):
        self.per_channel_blacklist = \
                dict((chan, set(blist))
                     for (chan, blist) in self.eterno_blacklist.iteritems())

    def saveState(self):
        return self.per_channel_blacklist

    def loadState(self, state):
        self.per_channel_blacklist = state

    def command_blacklist(self, bot, user, chan, args):
        bl = self.per_channel_blacklist.setdefault(chan, set())
        if len(args) == 0:
            return bot.address_msg(user, chan,
                    'usage: "blacklist me" OR "blacklist [name [name2 [...]]]". '
                    'Second form requires log_blacklist_admin privilege in this '
                    'channel. Shell-style wildcards are ok.')
        if len(args) == 1 and args[0] in ('me', user):
            bl.add(user)
            return bot.address_msg(user, chan, 'Blacklisting you for %s.' % chan)
        if bot.service.auth.channelUserHas(chan, user, 'log_blacklist_admin'):
            added = []
            for arg in args:
                if arg not in bl:
                    bl.add(arg)
                    added.append(arg)
            return bot.address_msg(user, chan, 'Blacklisted %s'
                                               % natural_list(map(repr, added)))
        return bot.address_msg(user, chan,
                'blacklisting other names requires the log_blacklist_admin '
                'privilege in this channel.')

    def command_unblacklist(self, bot, user, chan, args):
        bl = self.per_channel_blacklist.setdefault(chan, set())
        if len(args) == 0:
            return bot.address_msg(user, chan,
                    'usage: "unblacklist me" OR "unblacklist [name [name2 [...]]]". '
                    'Second form requires log_blacklist_admin privilege in this '
                    'channel. Shell-style wildcards are ok.')
        if len(args) == 1 and args[0] in ('me', user):
            if user in bl:
                bl.discard(user)
                return bot.address_msg(user, chan, 'Unblacklisting you for %s.' % chan)
            return bot.address_msg(user, chan, 'You are not blacklisted in %s.' % chan)
        if bot.service.auth.channelUserHas(chan, user, 'log_blacklist_admin'):
            found = []
            for arg in args:
                if arg in bl:
                    bl.discard(arg)
                    found.append(arg)
            return bot.address_msg(user, chan, 'Unblacklisted %s'
                                               % natural_list(map(repr, found)))
        return bot.address_msg(user, chan,
                'unblacklisting other names requires the log_blacklist_admin '
                'privilege in this channel.')

    def command_show(self, bot, user, chan, args):
        if len(args) == 1 and args[0] == 'blacklist':
            bl = map(repr, sorted(self.per_channel_blacklist.get(chan, ())))
            return bot.address_msg(user, chan, 'Blacklist for %s: %s'
                                               % (chan, natural_list(bl)))

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
        if user not in self.per_channel_blacklist.get(chan, ()):
            self.irclog('[%s] * %s %s' % (chan, user, data))

    def privmsg(self, bot, user, channel, msg):
        user = user.split('!', 1)[0]
        if user not in self.per_channel_blacklist.get(chan, ()):
            self.irclog('[%s] <%s> %s' % (channel, user, msg))
