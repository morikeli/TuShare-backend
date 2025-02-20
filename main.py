from fastapi import FastAPI
from db.database import Base, engine
from auth import router as auth_router
from users import router as users_router
from rides import router as rides_router
from fastapi.staticfiles import StaticFiles


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount("/media/dps", StaticFiles(directory="media/dps"), name="uploads")

app.include_router(auth_router, prefix='/api/v1/auth')
app.include_router(users_router, prefix='/api/v1/users')
app.include_router(rides_router, prefix='/api/v1')