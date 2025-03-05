# 🚀 TuShare (ride-sharing app) API

This is a FastAPI-based RESTful API for user signup and profile management. The API serves the [TuShare mobile app](https://github.com/morikeli/TuShare) and allows allows users to create accounts, login, view or edit their profile. 

## 📋 Features

- Create a new user account with required fields: first name, last name, username, email, gender, and password.
- Optional profile image upload.
- Password hashing for enhanced security.
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

