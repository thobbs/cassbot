from cassbot import BaseBotPlugin
from twisted.web import client, error
from twisted.internet import defer

class BuildCommand(BaseBotPlugin):
    build_token = 'xxxxxxxxxxxx'
    build_url = 'http://hudson.zones.apache.org/hudson/job'

    @defer.inlineCallbacks
    def command_build(self, bot, user, channel, args):
        if not args:
            yield bot.msg(channel, "usage: build <buildname>")
            return
        url = '%s/%s/polling?token=%s' % (self.build_url, args[0], self.build_token)
        msg = "request sent!"
        try:
            res = yield client.getPage(url)
        except error.Error, e:
            # Hudson returns a 404 even when this request succeeds :/
            if e.status == '404':
                pass
            else:
                msg = str(e)
        bot.address_msg(user, channel, msg)


