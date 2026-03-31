# 📦 KanMind Backend

Eine REST API für die Verwaltung von Kanban-Boards, gebaut mit Django REST Framework.

## 🛠️ Voraussetzungen

Stelle sicher, dass folgendes auf deinem Computer installiert ist:

- [Python 3.x](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)

## 🚀 Installation – Schritt für Schritt

### 1. Repository clonen

Öffne dein Terminal (oder die Eingabeaufforderung) und führe folgenden Befehl aus:

```bash
git clone https://github.com/NicoMeyerDev/kanmind-backend
```

Danach in den Projektordner wechseln:

```bash
cd kanmind-backend
```

### 2. Virtual Environment erstellen & aktivieren

Ein Virtual Environment sorgt dafür, dass die installierten Pakete nur für dieses Projekt gelten.

**Virtual Environment erstellen:**
```bash
python -m venv env
```

**Virtual Environment aktivieren:**

- Windows:
```bash
.\env\Scripts\Activate.ps1
```

- Mac/Linux:
```bash
source env/bin/activate
```

> ✅ Du erkennst, dass es funktioniert hat, wenn am Anfang deiner Kommandozeile **(env)** steht.

### 3. Abhängigkeiten installieren

Installiere alle benötigten Pakete aus der `requirements.txt`:

```bash
pip install -r requirements.txt
```

> ⚠️ Diese Datei ist nicht auf GitHub vorhanden, da sie geheime Daten enthält. Du musst sie manuell erstellen!


### 4. Datenbank einrichten

Da das Projekt SQLite verwendet, musst du **keine** extra Datenbank installieren. Führe einfach folgenden Befehl aus:

```bash
python manage.py migrate
```

> ℹ️ Ein `makemigrations` ist **nicht nötig**, da die Migrationsdateien bereits im Projekt enthalten sind. `migrate` reicht aus.

### 5. Server starten

```bash
python manage.py runserver
```

Die API ist jetzt erreichbar unter:

```
http://127.0.0.1:8000/
```
