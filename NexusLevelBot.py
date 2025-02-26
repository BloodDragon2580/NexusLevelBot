import nextcord
from nextcord.ext import commands, tasks
import json
import os
import time
import random

# Bot-Setup
TOKEN = "DEIN_BOT_TOKEN"
GUILD_ID = 123456789012345678  # Ersetze mit deiner Server-ID
LEVEL_UP_CHANNEL_ID = 123456789012345678  # ID des Channels für Level-Up-Nachrichten
QUIZ_CHANNEL_ID = 123456789012345678  
XP_PER_MESSAGE = 2
XP_PER_LEVEL = 30
XP_QUIZ_CORRECT = 10  
MAX_LEVEL = 100
XP_LOSS_PERCENTAGE = 0.1  # 10% XP-Verlust nach Inaktivität
INACTIVITY_TIME = 7 * 24 * 60 * 60  # 7 Tage in Sekunden

# Daten speichern/laden
DATA_FILE = "xp_data.json"
QUIZ_FILE = "quiz_data.json"

def load_data(file):
    if not os.path.exists(file) or os.stat(file).st_size == 0:
        return {}  # Falls die Datei nicht existiert oder leer ist, gib ein leeres Dict zurück
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data, file):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

xp_data = load_data(DATA_FILE)
quiz_data = load_data(QUIZ_FILE)

# Bot-Instanz mit vollständigen Intents
intents = nextcord.Intents.all()
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

# Nachricht-XP mit Anti-Spam-Schutz
user_last_message = {}  # Speichert die letzte Nachricht jedes Nutzers

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Anti-Spam-Schutz: Prüft, ob die Nachricht fast identisch zur letzten ist oder zu kurz
    user_id = message.author.id
    content = message.content.strip().lower()

    if user_id in user_last_message:
        last_content, last_time = user_last_message[user_id]
        if content == last_content or len(content) < 5 or time.time() - last_time < 5:
            return  # Kein XP für Spam-Nachrichten oder sehr kurze Nachrichten

    user_last_message[user_id] = (content, time.time())  # Letzte Nachricht speichern

    await bot.process_commands(message)  # Befehle zuerst verarbeiten

    level_up = add_xp(user_id, XP_PER_MESSAGE)
    save_data(xp_data, DATA_FILE)

    if level_up:
        channel = bot.get_channel(LEVEL_UP_CHANNEL_ID)
        if channel:
            await channel.send(f"🎉 Glückwunsch {message.author.mention}! Du hast nun das Level {level_up} erreicht! 🎉")

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
        save_data(xp_data, DATA_FILE)

class QuizView(nextcord.ui.View):
    def __init__(self, question_data):
        super().__init__(timeout=3600)  # 3600 Sekunden = 1 Stunde
        self.correct_index = question_data["correct"]
        self.question = question_data["question"]
        self.answers = question_data["answers"]
        self.message = None  # Speichert die Nachricht für spätere Bearbeitung

        for i, answer in enumerate(self.answers):
            self.add_item(QuizButton(label=answer, index=i, correct_index=self.correct_index))

    async def on_timeout(self):
        """Wird nach 1 Stunde aufgerufen, um die Buttons zu deaktivieren."""
        for child in self.children:
            if isinstance(child, nextcord.ui.Button):
                child.disabled = True
        if self.message:
            await self.message.edit(view=self)

class QuizButton(nextcord.ui.Button):
    def __init__(self, label, index, correct_index):
        super().__init__(label=label, style=nextcord.ButtonStyle.primary)
        self.index = index
        self.correct_index = correct_index

    async def callback(self, interaction: nextcord.Interaction):
        user_id = str(interaction.user.id)

        # Richtige Antwort
        if self.index == self.correct_index:
            add_xp(user_id, XP_QUIZ_CORRECT)
            save_data(xp_data, DATA_FILE)
            await interaction.response.send_message(f"✅ Richtig! {XP_QUIZ_CORRECT} XP wurden dir gutgeschrieben.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Falsch! Versuch es beim nächsten Mal erneut.", ephemeral=True)

        # Buttons deaktivieren nach der ersten Antwort
        for child in self.view.children:
            if isinstance(child, nextcord.ui.Button):
                child.disabled = True
        await self.view.message.edit(view=self.view)

@tasks.loop(minutes=60)
async def quiz_task():
    channel = bot.get_channel(QUIZ_CHANNEL_ID)
    if not channel or not quiz_data:
        return

    question_data = random.choice(quiz_data)
    embed = nextcord.Embed(title="📜 Quizfrage!", description=question_data["question"], color=nextcord.Color.blue())
    view = QuizView(question_data)
    message = await channel.send(embed=embed, view=view)
    view.message = message  # Speichert die Nachricht in der View

# Bot-Startup
@bot.event
async def on_ready():
    print(f"Bot {bot.user} ist online!")
    quiz_task.start()
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
    embed.add_field(name="🎯 XP für ein Level-Up", value=f"{XP_PER_LEVEL} XP", inline=False)
    embed.add_field(name="📉 XP-Verlust bei Inaktivität", value=f"{int(XP_LOSS_PERCENTAGE * 100)}% nach 7 Tagen", inline=False)
    embed.add_field(name="🔝 Maximales Level", value=f"{MAX_LEVEL}", inline=False)
    embed.set_footer(text="© Nexus Gaming | Viel Spaß beim Sammeln von XP!")
    await interaction.response.send_message(embed=embed)

# Slash-Command für das XP-Leaderboard
@bot.slash_command(name="leaderboard", description="Zeigt die Top 10 Spieler mit den meisten XP.", guild_ids=[GUILD_ID])
async def leaderboard(interaction: nextcord.Interaction):
    if not xp_data:
        await interaction.response.send_message("Es gibt noch keine XP-Daten!")
        return

    # Sortiere die Nutzer nach XP (absteigend)
    sorted_users = sorted(xp_data.items(), key=lambda x: x[1]["xp"], reverse=True)[:10]
    embed = nextcord.Embed(title="🏆 XP Leaderboard", color=nextcord.Color.gold())

    for rank, (user_id, data) in enumerate(sorted_users, start=1):
        user = await bot.fetch_user(int(user_id))  # Nutzername abrufen
        embed.add_field(name=f"#{rank} {user.name}", value=f"🆙 Level {data['level']} | ⭐ {data['xp']} XP", inline=False)

    embed.set_footer(text="© Nexus Gaming | Wer wird die Nummer 1?")
    await interaction.response.send_message(embed=embed)

@bot.slash_command(name="botinfo", description="Zeigt alle Funktionen und Befehle des Bots.", guild_ids=[GUILD_ID])
async def botinfo(interaction: nextcord.Interaction):
    embed = nextcord.Embed(title="🤖 NexusLevelBot - Info", color=nextcord.Color.blue())
    embed.add_field(
        name="📌 Funktionen",
        value=(
            "- Vergibt XP für Nachrichten mit Anti-Spam-Schutz\n"
            "- Levelaufstiege mit Benachrichtigung\n"
            "- XP-Verlust bei Inaktivität (nach 7 Tagen)\n"
            "- Leaderboard mit den Top 10 Spielern\n"
            "- Slash-Befehle für einfaches Handling"
        ),
        inline=False
    )
    embed.add_field(
        name="⚡ Befehle",
        value=(
            "`/level` → Zeigt dein aktuelles Level & XP an\n"
            "`/leaderboard` → Zeigt die Top 10 XP-Spieler\n"
            "`/info` → Erklärt das XP-System\n"
            "`/botinfo` → Zeigt diese Übersicht"
        ),
        inline=False
    )
    embed.set_footer(text="© Nexus Gaming | Viel Spaß beim Leveln! 🚀")
    await interaction.response.send_message(embed=embed)

# HIER DEN NEUEN QUIZTEST-BEFEHL EINFÜGEN
@bot.slash_command(name="quiztest", description="Startet ein Test-Quiz (nur für Administratoren).", guild_ids=[GUILD_ID])
async def quiztest(interaction: nextcord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Du hast keine Berechtigung, diesen Befehl zu nutzen!", ephemeral=True)
        return
    
    channel = bot.get_channel(QUIZ_CHANNEL_ID)
    if not channel or not quiz_data:
        await interaction.response.send_message("❌ Kein Quiz verfügbar oder Kanal nicht gefunden!", ephemeral=True)
        return

    question_data = random.choice(quiz_data)
    embed = nextcord.Embed(title="📜 Test-Quizfrage!", description=question_data["question"], color=nextcord.Color.green())
    view = QuizView(question_data)
    message = await channel.send(embed=embed, view=view)
    view.message = message
    
    await interaction.response.send_message("✅ Test-Quiz wurde gestartet!", ephemeral=True)

# Bot starten
bot.run(TOKEN)
