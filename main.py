from fastapi import FastAPI
from database import Base, engine
from auth import router as auth_router
from users import router as users_router
from rides import router as rides_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(rides_router)