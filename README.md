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
bot.run(TOKEN)
```

---

## 📌 4. Bot als Windows-Dienst mit NSSM einrichten

1. Lade [NSSM](https://nssm.cc/download) herunter und entpacke es.  
2. Öffne eine **Eingabeaufforderung mit Administratorrechten**.  
3. Wechsle in den NSSM-Ordner und installiere den Dienst mit folgendem Befehl (Dienstname **NexusLevelBot**):

   ```sh
   nssm install NexusLevelBot
   ```

4. Im erscheinenden Fenster:
   - Setze den **Pfad zur Python-Exe** (z.B. `C:\Python39\python.exe`)
   - Setze als **Argumente** den Pfad zu deiner `bot.py` (z.B. `C:\Pfad\zu\deinem\bot.py`)
   - Optional: Gib einen Startordner an, falls benötigt
5. Klicke auf **"Install Service"**.  
6. Starte den Dienst mit:

   ```sh
   nssm start NexusLevelBot
   ```

Der Bot läuft nun dauerhaft im Hintergrund als Windows-Dienst!

---

## 📌 5. Bot starten (ohne NSSM)

Falls du den Bot manuell starten möchtest, öffne das Terminal im Verzeichnis, in dem sich `bot.py` befindet, und führe aus:

```sh
python bot.py
```

---

Falls du Fragen hast oder Erweiterungen möchtest, sag einfach Bescheid!
