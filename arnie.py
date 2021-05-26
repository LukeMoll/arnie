import re
import znc # type: ignore[import]
import traceback

class arnie(znc.Module):
    module_types = [znc.CModInfo.NetworkModule]
    description = "Makes bridged messages appear more natural"

    # Module hooks

    def OnLoad(self, sArgsi, sMessage):
        self.load_channels()
        self.load_nicks()
        return True

    regex = re.compile("^<(?:\x03" + r"\d{,2}(?:,\d{,2})?)?([a-z[\]`_^|{}\\][a-z0-9[\]`_^|{}\\]*)" + "\x0F> ?", re.IGNORECASE)

    def OnChanTextMessage(self, Message):
        try:
            if (
                    self.match_nick(Message.GetNick()) and
                    self.match_channel(Message.GetChan())
                ):
                t = self.split_message(Message)
                if t is not None:
                    (nick, msgtext) = t
                    Message.SetText(msgtext)
                    Message.GetNick().SetNick(self.get_prefix() + nick + self.get_suffix())
        except Exception as e:
            self.PutModule("An error occurred. Please include the following in your report:")
            self.PutModule(traceback.format_exc())
        return znc.CONTINUE

    def OnModCommand(self, command):
        try:
            command = command.lower()
            tokens = re.split(r"\s", command)
            cmd_name = tokens[0]
            if cmd_name == "chan" or cmd_name =="channels":
                if len(tokens) < 2:
                    self.PutModule(self.usage["channels"])
                    return True
                elif tokens[1] == "clear":
                    self.clear_channels()
                    return True
                # else:
                params = set(tokens[2:])
                if  tokens[1] == "add":
                    self.add_channels(params)
                elif tokens[1] == "remove":
                    self.remove_channels(params)
                else:
                    self.PutModule(self.usage["channels"])

            elif cmd_name == "nick" or cmd_name == "nicks":
                if len(tokens) < 2:
                    self.PutModule(self.usage["nicks"])
                    return True
                elif tokens[1] == "clear":
                    self.clear_nicks()
                    return True
                # else:
                params = set(tokens[2:])
                if  tokens[1] == "add":
                    self.add_nicks(params)
                elif tokens[1] == "remove":
                    self.remove_nicks(params)
                else:
                    self.PutModule(self.usage["nicks"])

            elif cmd_name == "suffix":
                if len(tokens) < 2:
                    self.PutModule(self.usage["suffix"])
                    return True
                elif tokens[1] == "set":
                    self.set_suffix(" ".join(tokens[2:]))
                elif tokens[1] == "clear":
                    self.set_suffix("")
                else:
                    self.PutModule(self.usage["suffix"])

            elif cmd_name == "prefix":
                if len(tokens) < 2:
                    self.PutModule(self.usage["prefix"])
                    return True
                elif tokens[1] == "set":
                    self.set_prefix(" ".join(tokens[2:]))
                elif tokens[1] == "clear":
                    self.set_prefix("")
                else:
                    self.PutModule(self.usage["prefix"])

            elif cmd_name == "status":
                self.PutModule(
                    "Prefix: {}".format(self.get_prefix())
                    if len(self.get_prefix()) > 0
                    else "Empty prefix"
                )
                self.PutModule(
                    "Suffix: {}".format(self.get_suffix())
                    if len(self.get_suffix()) > 0
                    else "Empty suffix"
                )
                self.PutModule("Translating messages sent in:")
                self.PutModule(", ".join(self.channels))
                self.PutModule("and sent by:")
                self.PutModule(", ".join(self.nicks))

            elif cmd_name == "help":
                if len(tokens) == 1:
                    self.PutModule("Available commands:")
                    self.PutModule(", ".join(self.usage.keys()))
                    self.PutModule("Use `help <command>` to get more information about a command")
                elif tokens[1] in self.usage:
                    self.PutModule(self.usage[tokens[1]])
                else:
                    self.PutModule("No such command {}.".format(tokens[1]))

            else:
                self.PutModule("No such command!")
            return True
        except Exception as e:
            self.PutModule("An error occurred. Please include the following in your report:")
            self.PutModule(traceback.format_exc())
        return True

    usage = {
"channels": 
"""(chan for short)
channels add <channels>:    Adds all of <channels> (space separated) to the channel whitelist. Arnie will only translate messages sent in channels from the channel whitelist. Channels must be preceeded by a #.
channels remove <channels>:    Removes all of <channels> from the whitelist.
channels clear:    Removes all channels from the whitelist. No messages will be translated if the whitelist is empty.
""",
"nicks": 
"""(nick for short)
nicks add <nicks>:    Adds all of <nicks> (space separated) to the nick whitelist. Arnie will only translate messages sent by bots in the nick whitelist.
nicks remove <nicks>:    Removes all of <nicks> from the whitelist.
nicks clear:    Removes all nicks from the whitelist. No messages will be translated if the whitelist is empty.
""",
"prefix":
"""Appears before the username of the bridged user.
prefix set <prefix>:    Sets the prefix.
prefix clear:    Clears the prefix.
""",
"suffix": 
"""Appears after the username of the bridged user.
suffix set <suffix>:    Sets the suffix.
suffix clear:    Clears the suffix.
""",
"status": "Shows information about Arnie (takes no arguments)."
    }

    # Helper functions

    def split_message(self, Message):
        text = Message.GetText()
        match = re.match(self.regex, text)        
        if match is not None:
            nick = match.group(1)
            remaining_text = text[match.span()[1]:]
            return (nick, remaining_text)
        else:
            return None

    def match_nick(self, Nick):
        return Nick.GetNick().lower() in self.nicks

    def match_channel(self, Channel):
        return Channel.GetName().lower() in self.channels


    # Member accessors 
    def load_nicks(self):
        try:
            self.nicks = set(self.nv['nicks'].split(","))
        except KeyError:
            self.nicks = set()
        return self.nicks

    def add_nicks(self, nicks):
        nicks = {n.replace(",","") for n in nicks}
        self.nicks.update(nicks)
        self.nv['nicks'] = ",".join(self.nicks)

    def remove_nicks(self, nicks):
        nicks = {n.replace(",","") for n in nicks}
        self.nicks.difference_update(nicks)
        self.nv['nicks'] = ",".join(self.nicks)

    def clear_nicks(self):
        self.nv['nicks'] = ""
        self.nicks = set()


    def load_channels(self):
        try:
            self.channels = set(self.nv['channels'].split(","))
        except KeyError:
            self.channels = set()
        return self.channels

    def add_channels(self, channels):
        channels = {c.replace(",","") for c in channels}
        self.channels.update(channels)
        self.nv['channels'] = ",".join(self.channels)

    def remove_channels(self, channels):
        channels = {c.replace(",","") for c in channels}
        self.channels.difference_update(channels)
        self.nv['channels'] = ",".join(self.channels)

    def clear_channels(self):
        self.nv['channels'] = ""
        self.channels = set()
        
    
    def get_suffix(self):
        try:
            return self.nv['suffix']
        except KeyError:
            self.nv['suffix'] = ""
            return ""

    def set_suffix(self, suff):
        self.nv['suffix'] = suff

    def get_prefix(self):
        try:
            return self.nv['prefix']
        except KeyError:
            self.nv['prefix'] = ""
            return ""

    def set_prefix(self, pref):
        self.nv['prefix'] = pref