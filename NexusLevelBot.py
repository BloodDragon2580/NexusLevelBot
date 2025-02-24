import nextcord
from nextcord.ext import commands, tasks
import json
import os
import time

# Bot-Setup
TOKEN = "DEIN_BOT_TOKEN"
GUILD_ID = 123456789012345678  # Ersetze mit deiner Server-ID
LEVEL_UP_CHANNEL_ID = 123456789012345678  # ID des Channels für Level-Up-Nachrichten
XP_PER_MESSAGE = 5
XP_PER_VOICE_MINUTE = 2
XP_PER_LEVEL = 20
MAX_LEVEL = 100
XP_LOSS_PERCENTAGE = 0.1  # 10% XP-Verlust nach Inaktivität
INACTIVITY_TIME = 7 * 24 * 60 * 60  # 7 Tage in Sekunden

# Daten speichern/laden
DATA_FILE = "xp_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

xp_data = load_data()

# Bot-Instanz mit Intents
intents = nextcord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(intents=intents)

# XP hinzufügen & letzte Aktivität speichern
def add_xp(user_id, amount):
    user_id = str(user_id)

    if user_id not in xp_data:
        xp_data[user_id] = {"xp": 0, "level": 1, "last_active": time.time()}

    xp_data[user_id]["xp"] += amount
    xp_data[user_id]["last_active"] = time.time()  # Letzte Aktivität aktualisieren

    current_level = xp_data[user_id]["level"]
    new_level = min(xp_data[user_id]["xp"] // XP_PER_LEVEL + 1, MAX_LEVEL)

    if new_level > current_level:
        xp_data[user_id]["level"] = new_level
        return new_level
    return None

# Nachricht-XP
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    level_up = add_xp(message.author.id, XP_PER_MESSAGE)
    save_data(xp_data)

    if level_up:
        channel = bot.get_channel(LEVEL_UP_CHANNEL_ID)
        if channel:
            await channel.send(f"🎉 {message.author.mention} hat Level {level_up} erreicht! 🎉")

    await bot.process_commands(message)

# Sprachkanal-XP
@bot.event
async def on_voice_state_update(member, before, after):
    if not before.channel and after.channel:
        add_xp(member.id, XP_PER_VOICE_MINUTE)
        save_data(xp_data)

# XP-Verlust bei Inaktivität (wird jede Stunde überprüft)
@tasks.loop(hours=1)
async def check_inactivity():
    current_time = time.time()
    changed = False

    for user_id, data in xp_data.items():
        last_active = data.get("last_active", 0)
        if current_time - last_active > INACTIVITY_TIME:  # Mehr als 7 Tage inaktiv
            old_xp = data["xp"]
            xp_loss = max(int(old_xp * XP_LOSS_PERCENTAGE), 1)  # Mindestens 1 XP verlieren
            data["xp"] = max(old_xp - xp_loss, 0)  # XP darf nicht negativ werden

            # Level-Update
            new_level = data["xp"] // XP_PER_LEVEL + 1
            if new_level < data["level"]:
                data["level"] = new_level

            changed = True

    if changed:
        save_data(xp_data)

# Bot-Startup
@bot.event
async def on_ready():
    print(f"Bot {bot.user} ist online!")
    check_inactivity.start()  # XP-Verlust starten

# Slash-Command für XP & Level
@bot.slash_command(name="level", description="Zeigt dein aktuelles Level und XP an.", guild_ids=[GUILD_ID])
async def check_level(interaction: nextcord.Interaction):
    user_id = str(interaction.user.id)
    if user_id in xp_data:
        xp = xp_data[user_id]["xp"]
        level = xp_data[user_id]["level"]
        await interaction.response.send_message(f"{interaction.user.mention}, du hast {xp} XP und bist Level {level}.")
    else:
        await interaction.response.send_message(f"{interaction.user.mention}, du hast noch keine XP gesammelt.")

# Slash-Command für Info mit Copyright
@bot.slash_command(name="info", description="Zeigt alle Informationen zum XP-System.", guild_ids=[GUILD_ID])
async def info(interaction: nextcord.Interaction):
    embed = nextcord.Embed(title="📜 XP & Level System Infos", color=nextcord.Color.blue())
    embed.add_field(name="📩 XP pro Nachricht", value=f"{XP_PER_MESSAGE} XP", inline=False)
    embed.add_field(name="🎙 XP pro Minute im Sprachkanal", value=f"{XP_PER_VOICE_MINUTE} XP", inline=False)
    embed.add_field(name="🎯 XP für ein Level-Up", value=f"{XP_PER_LEVEL} XP", inline=False)
    embed.add_field(name="📉 XP-Verlust bei Inaktivität", value=f"{int(XP_LOSS_PERCENTAGE * 100)}% nach 7 Tagen", inline=False)
    embed.add_field(name="🔝 Maximales Level", value=f"{MAX_LEVEL}", inline=False)
    
    embed.set_footer(text="© Nexus Gaming | Viel Spaß beim Sammeln von XP!")

    await interaction.response.send_message(embed=embed)

# Bot starten
bot.run(TOKEN)
```

---

## 📌 4. Bot starten  
Öffne das Terminal im Verzeichnis, wo sich `bot.py` befindet, und starte den Bot mit:  
```sh
python bot.py
```

Falls du Fragen hast oder Erweiterungen möchtest, sag einfach Bescheid!
Das kannst du direkt als README.md in GitHub verwenden.






Du:
Bitte das bot Script in eine extra Code Box. Also Anleitung eine Box und Script eine Box 
ChatGPT:
Hier ist die README.md-Datei mit der Anleitung in einer Code-Box und dem Bot-Skript in einer separaten Code-Box.

md
Code kopieren
# 🎮 Discord XP & Level Bot (Nextcord)

Ein Discord-Bot auf **Python-Basis mit nextcord**, der XP und Level für Nachrichten und Sprachaktivitäten vergibt.  
✅ **XP für Nachrichten & Sprachchat**  
✅ **Level-Up mit Benachrichtigung**  
✅ **Slash-Commands (`/level` & `/info`)**  
✅ **XP-Verlust nach 7 Tagen Inaktivität**  
✅ **Maximales Level von 100**  
✅ **Copyright: `© Nexus Gaming`**  

---

## 📌 1. Bot im Discord Developer Portal erstellen  

1. Gehe auf [Discord Developer Portal](https://discord.com/developers/applications)  
2. Klicke auf **"New Application"** und gib einen Namen ein  
3. Gehe zum Tab **"Bot"** und klicke auf **"Add Bot"**  
4. **Kopiere den Token** (brauchen wir später für den Code)  
5. **Aktiviere diese Intents:**  
   - ✅ `MESSAGE CONTENT INTENT`  
   - ✅ `SERVER MEMBERS INTENT`  
   - ✅ `PRESENCE INTENT`  

6. Gehe zum Tab **OAuth2 > URL Generator**  
   - Wähle **"bot"** und **"applications.commands"**  
   - Setze diese Berechtigungen:  
     ✅ `Send Messages`  
     ✅ `Read Messages`  
     ✅ `Use Slash Commands`  
     ✅ `Connect` & `Speak` (für Voice-Tracking)  
   - Kopiere die generierte URL und füge den Bot zu deinem Server hinzu  

---

## 📌 2. Benötigte Pakete installieren  

Öffne das Terminal oder die Eingabeaufforderung und installiere die notwendigen Python-Bibliotheken:  

```sh
pip install nextcord pynacl
```

Falls `pip` nicht erkannt wird, versuche:  
```sh
python -m pip install nextcord pynacl
```

---

## 📌 3. Vollständiger Code für den Bot  

Speichere diesen Code als **`bot.py`**:  
````python
import nextcord
from nextcord.ext import commands, tasks
import json
import os
import time

# Bot-Setup
TOKEN = "DEIN_BOT_TOKEN"
GUILD_ID = 123456789012345678  # Ersetze mit deiner Server-ID
LEVEL_UP_CHANNEL_ID = 123456789012345678  # ID des Channels für Level-Up-Nachrichten
XP_PER_MESSAGE = 5
XP_PER_VOICE_MINUTE = 2
XP_PER_LEVEL = 20
MAX_LEVEL = 100
XP_LOSS_PERCENTAGE = 0.1  # 10% XP-Verlust nach Inaktivität
INACTIVITY_TIME = 7 * 24 * 60 * 60  # 7 Tage in Sekunden

# Daten speichern/laden
DATA_FILE = "xp_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

xp_data = load_data()

# Bot-Instanz mit Intents
intents = nextcord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(intents=intents)

# XP hinzufügen & letzte Aktivität speichern
def add_xp(user_id, amount):
    user_id = str(user_id)

    if user_id not in xp_data:
        xp_data[user_id] = {"xp": 0, "level": 1, "last_active": time.time()}

    xp_data[user_id]["xp"] += amount
    xp_data[user_id]["last_active"] = time.time()  # Letzte Aktivität aktualisieren

    current_level = xp_data[user_id]["level"]
    new_level = min(xp_data[user_id]["xp"] // XP_PER_LEVEL + 1, MAX_LEVEL)

    if new_level > current_level:
        xp_data[user_id]["level"] = new_level
        return new_level
    return None

# Nachricht-XP
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    level_up = add_xp(message.author.id, XP_PER_MESSAGE)
    save_data(xp_data)

    if level_up:
        channel = bot.get_channel(LEVEL_UP_CHANNEL_ID)
        if channel:
            await channel.send(f"🎉 {message.author.mention} hat Level {level_up} erreicht! 🎉")

    await bot.process_commands(message)

# Sprachkanal-XP
@bot.event
async def on_voice_state_update(member, before, after):
    if not before.channel and after.channel:
        add_xp(member.id, XP_PER_VOICE_MINUTE)
        save_data(xp_data)

# XP-Verlust bei Inaktivität (wird jede Stunde überprüft)
@tasks.loop(hours=1)
async def check_inactivity():
    current_time = time.time()
    changed = False

    for user_id, data in xp_data.items():
        last_active = data.get("last_active", 0)
        if current_time - last_active > INACTIVITY_TIME:  # Mehr als 7 Tage inaktiv
            old_xp = data["xp"]
            xp_loss = max(int(old_xp * XP_LOSS_PERCENTAGE), 1)  # Mindestens 1 XP verlieren
            data["xp"] = max(old_xp - xp_loss, 0)  # XP darf nicht negativ werden

            # Level-Update
            new_level = data["xp"] // XP_PER_LEVEL + 1
            if new_level < data["level"]:
                data["level"] = new_level

            changed = True

    if changed:
        save_data(xp_data)

# Bot-Startup
@bot.event
async def on_ready():
    print(f"Bot {bot.user} ist online!")
    check_inactivity.start()  # XP-Verlust starten

# Slash-Command für XP & Level
@bot.slash_command(name="level", description="Zeigt dein aktuelles Level und XP an.", guild_ids=[GUILD_ID])
async def check_level(interaction: nextcord.Interaction):
    user_id = str(interaction.user.id)
    if user_id in xp_data:
        xp = xp_data[user_id]["xp"]
        level = xp_data[user_id]["level"]
        await interaction.response.send_message(f"{interaction.user.mention}, du hast {xp} XP und bist Level {level}.")
    else:
        await interaction.response.send_message(f"{interaction.user.mention}, du hast noch keine XP gesammelt.")

# Slash-Command für Info mit Copyright
@bot.slash_command(name="info", description="Zeigt alle Informationen zum XP-System.", guild_ids=[GUILD_ID])
async def info(interaction: nextcord.Interaction):
    embed = nextcord.Embed(title="📜 XP & Level System Infos", color=nextcord.Color.blue())
    embed.add_field(name="📩 XP pro Nachricht", value=f"{XP_PER_MESSAGE} XP", inline=False)
    embed.add_field(name="🎙 XP pro Minute im Sprachkanal", value=f"{XP_PER_VOICE_MINUTE} XP", inline=False)
    embed.add_field(name="🎯 XP für ein Level-Up", value=f"{XP_PER_LEVEL} XP", inline=False)
    embed.add_field(name="📉 XP-Verlust bei Inaktivität", value=f"{int(XP_LOSS_PERCENTAGE * 100)}% nach 7 Tagen", inline=False)
    embed.add_field(name="🔝 Maximales Level", value=f"{MAX_LEVEL}", inline=False)
    
    embed.set_footer(text="© Nexus Gaming | Viel Spaß beim Sammeln von XP!")

    await interaction.response.send_message(embed=embed)

# Bot starten
bot.run(TOKEN)
