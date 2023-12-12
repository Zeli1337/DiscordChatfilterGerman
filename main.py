import json
import random as ran
import time
import os
import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands
from replit import db

from server import keep_alive

TOKEN = "### Token Here###"
intents = discord.Intents.all()
client = commands.Bot(command_prefix='.',
                      description="this is a test",
                      intents=intents)
current_time = time
blacklist = [
    "nutzer oder bots blacklisten"
]



verwarnungBan = 0
verwarnungMute = 0
verwarnungTimeout = 0



# Bots Aufgabe ist das Filtern von Beleidigungen und diese aus dem Server zu entfernen 
# im Englischsprachigen gibt es für jeweilge Problematik eine Bibliothek https://pypi.org/project/insults/ welche das manuelle hinzufügen von Beleidigungen 
# erübrigt. Da diese jedoch aber nur für englisschprachige Beleidigungen funktioniert wäre hier die einfachste Lösung selbst sich beleidigungen zu überlegen
# array kann gefüllt werden mit Beleidigungen welche auf dem Server gelöscht und verwarnt gehören
beleidigung = [
    "Arschloch"
]


#Api Schnittstelle für Nachrichten Artikel zu passendem Zeitfenster.
def get_news(keyword, date):
  news = requests.get(
      f"https://newsapi.org/v2/everything?q={keyword}&from={date}&sortBy=popularity&apiKey=a0281b7dd27b4fa9a2a56a5d5f8e4781"
  )
  json_data = json.loads(news.text)
  new = json_data["articles"]
  return "Titel: " + new[0]["title"] + "\nAutor: " + new[0][
      "author"] + "\nInhalt: " + new[0][
          "description"] + "\n Link zum Artikel: " + new[0]["url"]

#Api Schnittstelle für Zahlenfakten
def math_facts(number):
  number = requests.get(f"http://numbersapi.com/{number}")
  data = BeautifulSoup(number.text, "html.parser")
  return data




#Lyrics research
def get_lyric(artist, title):
  requests.get("https://api.lyrics.ovh/v1/artist/title")

#Quote APi
def get_quote():
  quote = requests.get("https://www.zenquotes.io/api/random")
  json_data = json.loads(quote.text)
  quote = json_data[0]['q'] + " ~ " + json_data[0]['a']
  return quote


@client.event
async def on_ready():
  print("Eingeloggt als {0.user}".format(client))


@client.command()
async def ping(ctx):
  await ctx.send("Pong!")


@client.command()
async def witz(ctx):
  await ctx.send(
      f'{str(ctx.author).split("#")[0]}, ich bin leider nicht lustig!')
  return


@client.command()  #fixen
async def Zelimirus(ctx):
  await ctx.send(
      f'{str(ctx.author).split("#")[0]}, <@211524621579583488> ist der Autor dieses Bots'
  )


@client.command()
async def random(ctx, span0, span1):
  await ctx.send(
      f'Hier ist deine Zufallszahl: {ran.randrange(int(span0), int(span1))}')


@client.command()  #
async def spenden(ctx):
  await ctx.send(
      f'{str(ctx.author).split("#")[0]}, dies kannst du im Twitch Stream in dem du ihm ein Abo darlässt'
  )


@client.command()
async def quote(ctx):
  await ctx.send(get_quote())




@client.command()
@commands.has_permissions(administrator=True)
async def VerwarnungenEntfernen(ctx, name):
  name = name.lower()
  if (name in db.keys()):
    del db[f'{name}']
    await ctx.send("Verwarnungen entfernt")
    print(db.keys())
    return
  await ctx.send("Keine Verwarnungen gefunden")
  print(db.keys())
  return


@client.command()
@commands.has_permissions(administrator=True)
async def Verwarnen(ctx, name):
  name = name.lower()
  if (str(name) not in db.keys()):
    db[f"{name}"] = 1
    print(db[f"{name}"])
  else:
    db[f"{name}"] += 1


@client.command()
@commands.has_permissions(administrator=True)
async def VerwarnungenAnzeigen(ctx, name):
  print(str(name))
  name = name.lower()
  if (name in db.keys()):
    await ctx.send(f"Der Nutzer {name} hat {db[f'{name}']} Verwarnungen")

    return
  await ctx.send("Keine Verwarnungen gefunden")

  return


@client.command()
@commands.has_permissions(administrator=True)
async def VerwarnungenStrafe(ctx, anzahlMute, anzahlTimeout, anzahlBan):
  verwarnungMute = anzahlMute
  verwarnungBan = anzahlBan
  verwarnungTimeout = anzahlTimeout
  await ctx.send(
      f" Strafmaß Mute {anzahlMute} Strafmaß Timeout {verwarnungTimeout} Strafmaß Ban {anzahlBan} der Wert 0 entspricht hier nicht aktiviert"
  )
  return

## Work in Progess -> automatischer Ban nach x Verwarnungen
async def strafen(userPunish):
  print(userPunish)
  print(db[userPunish])
  num = db[userPunish]
  if (num== verwarnungBan):
    print("ban")
    del db[userPunish]
    return
  elif (num == verwarnungTimeout):
    print("timeout")
    return
  elif (num == verwarnungMute):
    print("mute")
    return

## Textfilter um verbotnene Wörter zu entfernen
@client.listen('on_message')
async def filter(message):
  authorm = str(message.author).split('#')[0]
  user_message = str(message.content)

  if message.author == client.user:
    return
  if user_message.lower() in beleidigung:
    if ("<@" + str(message.author.id) + ">") not in db.keys():
      db[f"<@{str(message.author.id)}>"] = 1
      print(db[f"<@{str(message.author.id)}>"])
    else:
      db[f"<@{str(message.author.id)}>"] += 1
      await strafen(f"<@{str(message.author.id)}>")

    await message.channel.send(f"{message.author}, bitte keine Beleidigungen")
    await message.channel.send(
        f"Dies ist deine {db[f'<@{str(message.author.id)}>']}. Verwarnung")

    await message.delete()

    return


@client.command()
async def news(ctx, *args):
  await ctx.send(get_news(*args))



keep_alive()

client.run(TOKEN)
