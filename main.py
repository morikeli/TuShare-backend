from auth import router as auth_router
from contextlib import asynccontextmanager
from db.database import init_db
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from routers.messages import router as msg_router
from routers.rides import router as rides_router
from routers.users import router as users_router
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define an asynchronous lifespan context manager for the FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    print('======='*10)     # for decoration
    logger.info('STARTING UP ... Initializing database.')
    await init_db()     # initialize database
    logger.info('DONE ... Database initialized.')
    print('======='*10)     # for decoration

    # Yield control back to the FastAPI application — 
    # this allows the app to run while keeping the lifespan context open
    yield
    
    # this is displayed when the server is shutdown
    logger.info('SHUTTING DOWN ... Cleaning up resources')
    logger.info('Wohoo! ... CLEAN UP COMPLETE')


app = FastAPI(lifespan=lifespan)

app.mount("/media/dps", StaticFiles(directory="media/dps"), name="uploads")
app.include_router(auth_router, prefix='/api/v1/auth')
app.include_router(users_router, prefix='/api/v1/users')
app.include_router(rides_router, prefix='/api/v1')
app.include_router(msg_router, prefix='/api/v1')
