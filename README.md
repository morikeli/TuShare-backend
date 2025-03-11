# 🚀 TuShare (ride-sharing app) API
This FastAPI-based RESTful API powers the [TuShare mobile app](https://github.com/morikeli/TuShare).

## 📋 Features

- Authentication - login, signup & logout
- Profile management - view and update user profile
- Password hashing for enhanced security.
- Book rides, search for available rides and view booked rides
- In-app messaging between passengers and drivers
- Database integration using SQLAlchemy.
- Error handling for unique constraint violations.

---

## 🛠️ Tech Stack

- **FastAPI** - Python web framework for building REST APIs.
- **SQLite** - Database for data persistence.
- **SQLAlchemy** - ORM for database interactions.
- **Pydantic** - Data validation.
- **UUID** - Unique ID generation.
- **Shutil & OS** - File system operations.

---

## 📦 Installation

1. **Clone the repository:**

```bash
git clone https://github.com/morikeli/TuShare-backend.git
```

2. **Create a virtual environment and activate it:**

```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
venv\Scripts\activate    # On Windows
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Run the FastAPI server:**

```bash
uvicorn main:app --reload
```

The server will start at: `http://localhost:8000`

---

## 🧪 Testing

You can test the API using [Postman](https://www.postman.com/) or the FastAPI interactive docs:

```
http://localhost:8000/docs
```

---

## 🗂️ Project Structure

```
📦project-root
│
├── 📄 auth.py
├── 📄 config.py
├── 📄 main.py
├── 📄 models.py
├── 📄 __init__.py
├── 📄 database.py
│   └── 📄 __init__.py
│   └── 📄 database.py
│   └── 📄 schemas.py
│   └── 📄 seed_db.py
├── 📄 routes
│   └── 📄 __init__.py
│   └── 📄 messages.py
│   └── 📄 rides.py
│   └── 📄 users.py
├── 📂 media
│   └── 📂 dps
├── 📄 .env
├── 📄 .gitignore
├── ⚙️ alembic.ini
├── 📄 requirements.txt
└── 📄 README.md
├── 📄 utils.py
```

---

## 📌 License

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

---

## 🐛 Issues

If you encounter any issues, please create an issue [here](https://github.com/morikeli/TuShare-backend/issues).

---

✨ Happy Coding! 🚀

