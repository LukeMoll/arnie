import re
import znc
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
            if tokens[0] == "chan" or tokens[0] =="channels":
                if tokens[1] == "clear":
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
            elif tokens[0] == "nick" or tokens[0] == "nicks":
                if tokens[1] == "clear":
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
            elif tokens[0] == "suffix":
                if tokens[1] == "set":
                    self.set_suffix(" ".join(tokens[2:]))
                elif tokens[1] == "clear":
                    self.set_suffix("")
                else:
                    self.PutModule(self.usage["suffix"])
            elif tokens[0] == "prefix":
                if tokens[1] == "set":
                    self.set_prefix(" ".join(tokens[2:]))
                elif tokens[1] == "clear":
                    self.set_prefix("")
                else:
                    self.PutModule(self.usage["prefix"])
            elif tokens[0] == "status":
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
            elif tokens[0] == "help":
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
        "channels": "todo",
        "nicks": "todo",
        "suffix": "todo",
        "prefix": "todo"
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