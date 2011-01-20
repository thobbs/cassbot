from cassbot import BaseBotPlugin

class LogsCommand(BaseBotPlugin):
    logs_url = 'http://www.eflorenzano.com/cassbot/'

    def command_logs(self, bot, user, channel, args):
        return bot.address_msg(user, channel, self.logs_url)
