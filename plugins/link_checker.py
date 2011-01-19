import re
from itertools import chain
from twisted.internet import defer
from cassbot import BaseBotPlugin

class CassandraLinkChecker(BaseBotPlugin):
    ticket_url_template = 'http://issues.apache.org/jira/browse/CASSANDRA-%d'
    commit_url_template = 'http://svn.apache.org/viewvc?view=rev&revision=%d'

    ticket_re = re.compile(r'(?:^|[]\s[(){}<>/:",-])(#{1,2})(\d+)\b')
    commit_re = re.compile(r'\br(\d+)\b')
    low_ticket_cutoff = 10

    def checktickets(self, msg):
        for match in self.ticket_re.finditer(msg):
            ticket = int(match.group(2))
            if ticket > self.low_ticket_cutoff or match.group(1) == '##':
                yield self.post_ticket(ticket)

    def post_ticket(self, ticket_num):
        return self.ticket_url_template % (ticket_num,)

    def checkrevs(self, msg):
        for match in self.commit_re.finditer(msg):
            commit = int(match.group(1))
            yield self.commit_url_template % (commit,)

    @defer.inlineCallbacks
    def privmsg(self, bot, user, channel, msg):
        for r in chain(self.checktickets(msg), self.checkrevs(msg)):
            yield bot.msg(channel, r)

    @defer.inlineCallbacks
    def action(self, bot, user, channel, msg):
        for r in chain(self.checktickets(msg), self.checkrevs(msg)):
            yield bot.msg(channel, r)
