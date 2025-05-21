# 🚀 TuShare (ride-sharing app) API
This FastAPI-based RESTful API powers the [TuShare mobile app](https://github.com/morikeli/TuShare).

## Project screenshots
![Screenshot from 2025-05-17 22-24-08](https://github.com/user-attachments/assets/d5e084bd-2370-4b2d-8197-9e8119e6f489)
![Screenshot from 2025-05-17 22-24-22](https://github.com/user-attachments/assets/c9bce08f-efb0-427c-b9c3-6c3a6c7dd268)
![Screenshot from 2025-05-17 22-24-32](https://github.com/user-attachments/assets/2510f77c-f8f1-44bb-9612-a42c6229c5c9)


## 📋 Features

- Authentication - login, signup & logout
- Profile management - view and update user profile
- Password hashing for enhanced security.
- Book rides, search for available rides and view booked rides
- In-app messaging between passengers and drivers
- Database integration using SQLAlchemy.
- Error handling for unique constraint violations.

---

## 🛠️ Tech stack

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
uvicorn app:app --reload
```

The server will start at: `http://localhost:8000`

---

## 🧪 Testing

You can test the API using [Postman](https://www.postman.com/) or the FastAPI interactive docs:

```
http://localhost:8000/api/v1/docs  # swagger docs
http://localhost:8000/api/v1/redoc  # redoc

```

---

## 🗂️ Project structure

```
📦project-root
│
├── 📂 app
│   └── 📂 core
|   |   └── 📄 __init__.py
|   |   └── 📄 config.py
|   |   └── 📄 database.py
|   |   └── 📄 dependencies.py
|   |   └── 📄 redis.py
|   |   └── 📄 token_bearer.py
│   └── 📂 mails
|   |   └── 📄 __init__.py
|   |   └── 📄 send_mail.py
│   └── 📂 middleware
|   |   └── 📄 __init__.py
|   |   └── 📄 auth_middleware.py
│   └── 📂 models
|   |   └── 📄 __init__.py
|   |   └── 📄 base.py
|   |   └── 📄 booking.py
|   |   └── 📄 messages.py
|   |   └── 📄 rides.py
|   |   └── 📄 user.py
│   └── 📂 routers
|   |   └── 📄 __init__.py
|   |   └── 📄 auth.py
|   |   └── 📄 messages.py
|   |   └── 📄 rides.py
|   |   └── 📄 users.py
│   └── 📂 schemas
|   |   └── 📄 __init__.py
|   |   └── 📄 auth_schema.py
|   |   └── 📄 booking_schema.py
|   |   └── 📄 messages_schema.py
|   |   └── 📄 rides_schema.py
|   |   └── 📄 user_schema.py
│   └── 📂 service
|   |   └── 📄 __init__.py
|   |   └── 📄 auth_service.py
|   |   └── 📄 booking_service.py
|   |   └── 📄 messages_service.py
|   |   └── 📄 rides_service.py
|   |   └── 📄 user_service.py
│   └── 📂 utils
|   |   └── 📄 __init__.py
|   └── 📄 __init__.py
|   └── 📄 exceptions.py
├── 📂 media
│   └── 📂 dps
├── 📄 migrations
│   └── 📄 
│   └── 📄 env.py
│   └── 📄 README.md
│   └── 📄 script.py.mako
├── 📄 scripts
│   └── 📄 __init__.py
│   └── 📄 seed_db.py
├── 📄 templates
│   └── 📄 email-verification.html
│   └── 📄 reset-password.html
|
├── 📄 .env
├── 📄 .gitignore
├── ⚙️ alembic.ini
├── 📄 auth.py
├── 📄 config.py
├── 📄 __init__.py
├── 📄 main.py
├── 📄 models.py
└── 📄 README.md
├── 📄 requirements.txt
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

> Made with ♥️. Don't hit the star button ⭐ to star this repo

✨ Happy Coding! 🚀

