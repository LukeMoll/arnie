Arnie
===

Arnie is a plugin for the [ZNC] IRC bouncer. It takes messages bridged into IRC (eg. from Slack) that look like this:

```
ldm: @sdhand how about this
ldm: four slices of bread
ldm: put fillings on 2 of them
ldm: and put the other 2 pieces of bread on top of the ones with fillings on
ldm: how many sandwiches
hackbot: <sdhand> ah, as in do you have a just a sandwich with extra bread
hackbot: <sdhand> or a sandwich sandwich
hackbot: <sdhand> it comes down to whether or not something can be both sandwich and filling
```
and makes them look more like this:
```
ldm: @sdhand how about this
ldm: four slices of bread
ldm: put fillings on 2 of them
ldm: and put the other 2 pieces of bread on top of the ones with fillings on
ldm: how many sandwiches
sdhand: ah, as in do you have a just a sandwich with extra bread
sdhand: or a sandwich sandwich
sdhand: it comes down to whether or not something can be both sandwich and filling
```

You can set a prefix or suffix to distinguish between IRC users and bridged users.

```
ldm: no, put 2 pieces of bread on a plate
ldm: put fillings on those 2 pieces of bread
ldm: and put a piece of bread on top of each of them
ldm: how many sandwiches is that
sdhand[s]: ye I got it
sdhand[s]: as I said, it comes down to whether or not you consider the inner sandwich
sdhand[s]: to be filling for the outer 2 pieces of bread
```

It will only translate messages from specified channels and users, so you don't need to worry about it interfering with non-bridged IRC channels. It also doesn't affect the `log` module so your IRC logs will also be unaffected.

## Installation
Installed as any other ZNC module. Requires [modpython] to be loaded

1. Copy `arnie.py` to the `modules` directory of your ZNC installation
2. Run `/msg *status loadmod arnie` to load the module
3. Send `help` to `*arnie` to get started.

## Usage
Full command help text is available by sending `help` to `*arnie`.