from cassbot import BaseBotPlugin, enabled_but_not_found, require_priv
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
        if len(args) != 1:
            yield bot.address_msg(user, channel, 'usage: modenable [modulename]')
            return
        bot.service.enable_plugin_by_name(args[0])
        yield bot.address_msg(user, channel, 'Module %s loaded.' % p.name())

    @require_priv('admin')
    @defer.inlineCallbacks
    def command_moddisable(self, bot, user, channel, args):
        if len(args) != 1:
            yield bot.address_msg(user, channel, 'usage: moddisable [modulename]')
            return
        if args[0] not in bot.service.pluginmap:
            yield bot.address_msg(user, channel, 'Module %s is not loaded.' % args[0])
            return
        bot.service.disable_plugin(args[0])
        yield bot.address_msg(user, channel, 'Module %s disabled.' % args[0])

    @require_priv('admin')
    @defer.inlineCallbacks
    def command_modreload(self, bot, user, channel, args):
        if len(args) == 0:
            yield bot.address_msg(user, channel, 'usage: modreload [modulenames]')
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
