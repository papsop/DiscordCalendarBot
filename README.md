# DiscordCalendarBot
This is a source code of my unofficial Discord TeamUP Calendar bot.
A guide on how to use the bot can be found here: [http://calbot.patrikpapso.com/](http://calbot.patrikpapso.com/)

If you wish to support me financially, you can do so via PayPal here: [paypal.me/bluexow](https://www.paypal.me/bluexow)

## How to run the bot
The bot runs on Python 3.7 and uses SQLite database to store data.
All the required libraries can be found in file `requirements.txt`.

To install all the required libraries run:
```
pip install -r requirements.txt
```

Save `config_example.py` as `config.py` and will in all the tokens
- Discord token from here: [https://discord.com/developers/applications](https://discord.com/developers/applications)
- TeamUP token from here: [https://teamup.com/api-keys/request](https://teamup.com/api-keys/request)

After that you can just run the `bot.py` file:
```
python bot.py
```
#### Free hosted version information
Hosted version of the bot is running on Raspberry pi zero W, uses virtualenv with libraries from `requirements.txt` and runs in [PM2](https://www.npmjs.com/package/pm2) process manager.
