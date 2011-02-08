import re
from twisted.internet import defer
from cassbot import BaseBotPlugin

class ZendeskLinkChecker(BaseBotPlugin):
    tickets_url = 'http://unconfigured.zendesk-url.com/tickets/'
    ticket_letter = 'z'

    def __init__(self):
        self.sprt_ticket_re = re.compile(r'\b%s([1-9][0-9]{0,4})\b' % self.ticket_letter)

    def loadState(self, conf):
        self.tickets_url = conf.get('tickets_url', self.tickets_url)
        self.ticket_letter = conf.get('ticket_letter', self.ticket_letter)
        self.sprt_ticket_re = re.compile(r'\b%s([1-9][0-9]{0,4})\b' % self.ticket_letter)

    def saveState(self):
        return {
            'tickets_url': self.tickets_url,
            'ticket_letter': self.ticket_letter
        }

    def check_for_references(self, msg):
        for match in self.sprt_ticket_re.finditer(msg):
            ticket = int(match.group(1))
            yield '%s%d' % (self.tickets_url, ticket)

    @defer.inlineCallbacks
    def privmsg(self, bot, user, channel, msg):
        for r in self.check_for_references(msg):
            yield bot.address_msg(user, channel, r, prefix=False)

    action = privmsg
