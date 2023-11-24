# last.fm Discord RPC

This is a small Python program that shows your currently playing last.fm song on your Discord profile!

# Quick start

Edit [config.py](config.py) to have your username (optionally a different Discord Client ID or last.fm API key).

```shell
$ pip install pypresence pylast
$ python main.py
```

Make sure to upload an asset you want displayed as the `loved` icon when using a different Discord Client ID.

# Issues

If you have any issues using the program, feel free to open an issue and let me know what's up, please make sure to provide as much info as you can! \
Or if you know what's going on you're also very welcome to open a PR and fix it yourself!

# `discord-gateway` Branch

This branch is used for an alternative version of the program (Currently WIP) that doesn't rely on your Discord Client
to tell Discord about your presence updates but rather does it through a Discord Gateway connection.

This has a few benefits:
 * It lets you run the program on another computer (Such as a Raspberry Pi) to make your status work on mobile/browser
 * Allows it to display "Listening to ..." instead of being limited to "Playing ..."

There's also some drawbacks:
 * This requires you to enter your Discord token which is inconvenient and also insecure
