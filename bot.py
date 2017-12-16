import pysher
import sys, time
import json
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

chats = [415734184]

pusher = pysher.Pusher("de504dc5763aeef9ff52")

prices = {"eur": 0, "usd": 0, "last": 0, "step": 100, "updated": time.time()}

def eur_callback(order):
    printer(order, "eur")

def usd_callback(order):
    printer(order, "usd")
    p = prices["last"] - prices["usd"]
    prices["updated"] = time.time()
    if abs(p) > prices["step"]:
        s = "Increase. " if p > 0 else "Decrease. "
        prices["last"] = round(prices["usd"] / prices["step"]) * prices["step"]
        s += "usd: %.0f, eur: %.0f" % (prices["usd"],prices["eur"])
        for chat in chats:
            bot.send_message(chat_id=chat, text=s)

def printer(order, currency):
    o = json.loads(order)
    prices[currency] = o["price"]
    print(currency, ": ", o["price"])

def connect_handler(data):
    channel_usd = pusher.subscribe('live_trades')
    channel_usd.bind('trade', usd_callback)
    channel_eur = pusher.subscribe('live_trades_btceur')
    channel_eur.bind('trade', eur_callback)

# BOT LOGIC
# TODO: mute command
def start(bot, update):
    if update.message.chat_id not in chats:
        chats.append(update.message.chat_id)
    print("connected user:", update.message.chat_id)
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

def echo(bot, update):
    if update.message.chat_id not in chats:
        chats.append(update.message.chat_id)
    print("connected user:", update.message.chat_id)
    s = "usd: %.0f, eur: %.0f (%.0f seconds ago)" % (prices["usd"],prices["eur"], time.time()-prices["updated"])
    print(update.message.text)
    bot.send_message(chat_id=update.message.chat_id, text=s)

with open("token", "r") as f:
    token = f.read()

bot = telegram.Bot(token=token)
print(bot.get_me())

updater = Updater(token=token)
dispatcher = updater.dispatcher
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()

pusher.connection.bind('pusher:connection_established', connect_handler)
pusher.connect()

updater.idle()
