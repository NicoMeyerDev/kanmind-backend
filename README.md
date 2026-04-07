# 📦 KanMind Backend

A RESTful backend API for managing Kanban boards, built with Django REST Framework.

## 🛠️ Requirements

Make sure the following is installed on your computer:

- [Python 3.12](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)

## 🚀 Installation – Step by Step

### 1. Clone the repository

Open your terminal (or command prompt) and run:

```bash
git clone https://github.com/NicoMeyerDev/kanmind-backend
```

Then navigate into the project folder:

```bash
cd kanmind-backend
```

### 2. Create and activate a virtual environment

A virtual environment ensures that the installed packages are only used for this project.

**Create the virtual environment:**
```bash
python -m venv env
```

**Activate the virtual environment:**

- **Windows**
```bash
.\env\Scripts\Activate.ps1
```

- **Mac/Linux**
```bash
source env/bin/activate
```

> ✅ You will know it worked when **(env)** appears at the beginning of your command line.

### 3. Install dependencies

Install all required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Set up the database

Since the project uses SQLite, you do **not** need to install a separate database.

Simply run:

```bash
python manage.py migrate
```

> ℹ️ Running `makemigrations` is **not necessary**, because the migration files are already included in the project. `migrate` is enough.

### 5. Start the server

```bash
python manage.py runserver
```

The API will then be available at:

```
http://127.0.0.1:8000/
```
