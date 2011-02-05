from cassbot import (BaseBotPlugin, enabled_but_not_found, require_priv,
                     require_priv_in_channel)
from twisted.internet import defer
from twisted.plugin import getModule

def makelist(i):
    return ', '.join(sorted(i)) if i else 'none'

class Admin(BaseBotPlugin):
    @defer.inlineCallbacks
    def command_modules(self, bot, user, channel, args):
        if args:
            yield bot.address_msg(channel, "usage: modules")
            return

        notfound = set()
        loaded = set()
        available = set()
        for name, p in bot.service.pluginmap.iteritems():
            if p is enabled_but_not_found:
                notfound.add(name)
            else:
                loaded.add(name)
        available = set(p.name() for p in bot.service.get_plugin_classes()) \
                    - notfound - loaded

        output = ['loaded modules: %s' % makelist(loaded)]
        if notfound:
            output.append('modules enabled but not found: %s' % makelist(notfound))
        output.append('other available modules: %s' % makelist(available))
        yield bot.address_msg(user, channel, '\n'.join(output))

    @require_priv('admin')
    @defer.inlineCallbacks
    def command_modenable(self, bot, user, channel, args):
        if len(args) == 0:
            yield bot.address_msg(user, channel, 'usage: modenable [modulenames]')
            return
        for arg in args:
            bot.service.enable_plugin_by_name(arg)
            yield bot.address_msg(user, channel, 'Module %s loaded.' % arg)

    @require_priv('admin')
    @defer.inlineCallbacks
    def command_moddisable(self, bot, user, channel, args):
        if len(args) == 0:
            yield bot.address_msg(user, channel, 'usage: moddisable [modulenames]')
            return
        for arg in args:
            if arg not in bot.service.pluginmap:
                yield bot.address_msg(user, channel, 'Module %s is not loaded.' % arg)
                continue
            bot.service.disable_plugin(arg)
            yield bot.address_msg(user, channel, 'Module %s disabled.' % arg)

    @require_priv('admin')
    @defer.inlineCallbacks
    def command_modreload(self, bot, user, channel, args):
        if len(args) == 0:
            yield bot.address_msg(user, channel, 'usage: modreload [modulenames]')
            return
        for arg in args:
            try:
                p = bot.service.pluginmap[arg]
            except KeyError:
                yield bot.address_msg(user, channel, 'Module %s is not loaded.' % arg)
                continue
            mod = getModule(p.__module__).load()
            reload(mod)
            bot.service.disable_plugin(arg)
            bot.service.enable_plugin_by_name(arg)
            yield bot.address_msg(user, channel, 'Module %s reloaded.' % arg)
