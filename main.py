import json
import random as ran
import time
import os
import discord
from discord.utils import get
import requests
from bs4 import BeautifulSoup
from discord.ext import commands
from replit import db
from datetime import timedelta

from server import keep_alive

TOKEN = 'BOT TOKEN HIER'
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix='.',
                      description="this is a test",
                      intents=intents)
current_time = time


# Bots Aufgabe ist das Filtern von Beleidigungen und diese aus dem Server zu entfernen 
# im Englischsprachigen gibt es für jeweilge Problematik eine Bibliothek https://pypi.org/project/insults/ welche das manuelle hinzufügen von Beleidigungen 
# erübrigt. Da diese jedoch aber nur für englisschprachige Beleidigungen funktioniert wäre hier die einfachste Lösung selbst sich beleidigungen zu überlegen
# array kann gefüllt werden mit Beleidigungen welche auf dem Server gelöscht und verwarnt gehören

beleidigung = [
    "Beleidigungen hier einfügen"
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





@client.command()
async def random(ctx, span0, span1):
  await ctx.send(
      f'Hier ist deine Zufallszahl: {ran.randrange(int(span0), int(span1))}')


@client.command()
async def quote(ctx):
  await ctx.send(get_quote())


@client.command()
@commands.has_permissions(administrator=True)
async def whelp(ctx):
  await ctx.send("Das Plugin besteht aus mehreren Befehlen")
  await ctx.send(".showconfig zeigt die Verwarnungsstrafmaße an")
  await ctx.send(
      ".changeconfig <anzWarnungenFürTimeout> <anzZeitinMinutenFürTimeout> <anzWarnungenFürMute> <anzWarnungenFürKick> <anzWarnungenFürBan> ändert die Verwarnungsstrafmaße 0 bedeutet aus"
  )
  await ctx.send(".deletewarnings @Name löscht die Warnungen eines Nutzers")
  await ctx.send(".warnings @Name zeigt die Warnungen eines Nutzers an")
  await ctx.send(".warn @Name warnt einen Nutzern")
  await ctx.send("Discord Bot by Zeli1337")
  return


@client.command()
@commands.has_permissions(administrator=True)
async def deletewarnings(ctx, name):
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
async def warn(ctx, name):
  name = name.lower()
  if (str(name) not in db.keys()):
    db[f"{name}"] = 1
    print(db[f"{name}"])
  else:
    db[f"{name}"] += 1
   


@client.command()
@commands.has_permissions(administrator=True)
async def warnings(ctx, name):
  print(str(name))
  name = name.lower()
  if (name in db.keys()):
    await ctx.send(f"Der Nutzer {name} hat {db[f'{name}']} Verwarnungen")
    
    return
  await ctx.send("Keine Verwarnungen gefunden")

  return


@client.command()
@commands.has_permissions(administrator=True)
async def showconfig(ctx):
  await ctx.send(
      f"Strafmaß Timeout {db['verwarnungTimeout']} - {db['TimeoutTime']}minuten\nStrafmaß Mute {db['verwarnungMute']}\nStrafmaß Kick{db['verwarnungKick']}\nStrafmaß Ban {db['verwarnungBan']}\nDer Wert 0 entspricht hier nicht aktiviert"
  )
  return


@client.command()
@commands.has_permissions(administrator=True)
async def changeconfig(ctx, anzahlTimeout,tt, anzahlMute, anzahlKick, anzahlBan):
  global verwarnungMute
  verwarnungMute = int(anzahlMute)
  db['verwarnungMute'] = anzahlMute
  db['verwarnungTimeout'] = anzahlTimeout
  db['verwarnungBan'] = anzahlBan
  db['TimeoutTime'] = tt
  db['verwarnungKick'] = anzahlKick
  await ctx.send("Verwarnungsgrößen geändert")
  await ctx.send(
    f"Strafmaß Timeout {db['verwarnungTimeout']} - {db['TimeoutTime']}minuten\nStrafmaß Mute {db['verwarnungMute']}\nStrafmaß Kick{db['verwarnungKick']}\nStrafmaß Ban {db['verwarnungBan']}\nDer Wert 0 entspricht hier nicht aktiviert"
  )
  return


async def strafen(userPunish, dm):
  member = dm.author
  print(userPunish)
  print(db[userPunish])
  num = int(db[userPunish])
  channel = client.get_channel("CHANNEL FÜR LOG NAME")

  if (num == int(db['verwarnungBan'])):
    print("ban")
    await channel.send(f"{userPunish} wurde soeben gebannt")
    del db[userPunish]
    member.ban(reason="Verwarnungungslimit überschritten")
    return
  elif(num == int(db['verwarnungKick'])):
    print("kick")
    await channel.send(f"{userPunish} wurde soeben gekickt")
    member.kick(reason="Verwarnungungslimit überschritten")
  elif (num == int(db['verwarnungMute'])):

    print("mute")
    await channel.send(f"{userPunish} wurde soeben permanent Stummgeschalten")
    guild = client.get_guild("GUILD ID")

    if guild:
      member = guild.get_member(dm.author.id)
      role = discord.utils.get(guild.roles, name='muted')

      if member and role:
        await member.add_roles(role)
        print(f"{member.display_name} has been given the {role.name} role.")
      else:
        print("Member or role not found.")
    else:
      print("Guild not found.")

  elif (num == int(db['verwarnungTimeout'])):
    print("timeout")
    await channel.send(f"{userPunish} wurde soeben für {int(db['TimeoutTime'])}min Stummgeschalten")
    await member.timeout(timedelta(minutes=int(db['TimeoutTime'])), reason="Verwarnung")

    return

  


@client.listen('on_message')
async def filter(message):
  dmDc = message.content.lower().split(' ')
  user_message = str(message.content)

  if message.author == client.user or message.author == 'ProBot ✨#5803':
    return
  for item in dmDc:
    if item in beleidigung:
      if ("<@" + str(message.author.id) + ">") not in db.keys():
        db[f"<@{str(message.author.id)}>"] = 1
        print(db[f"<@{str(message.author.id)}>"])
        channel = client.get_channel(1184114595724533760)
        await channel.send(f" Der Nutzer <@{str(message.author.id)}> hat soeben eine Verwarnung erhalten")
      else:
        db[f"<@{str(message.author.id)}>"] += 1
        channel = client.get_channel(1184114595724533760)
        await channel.send(f" Der Nutzer <@{str(message.author.id)}> hat soeben eine Verwarnung erhalten")
        await strafen(f"<@{str(message.author.id)}>", message)

      await message.channel.send(f"{message.author}, bitte keine Beleidigungen"
                                 )
      await message.channel.send(
          f"Dies ist deine {db[f'<@{str(message.author.id)}>']}. Verwarnung")

      await message.delete()

    return


@client.command()
async def news(ctx, *args):
  await ctx.send(get_news(*args))




keep_alive()

client.run(TOKEN)
