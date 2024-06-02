import uvicorn
from fastapi import FastAPI

import data.storage.storage_initializer as storage
from config import DB_FILE_NAME
from routing.auth.routing import router as auth_router
from routing.device.routing import router as device_router

storage.initialize_storage(DB_FILE_NAME)
app = FastAPI()
app.include_router(device_router, prefix='/device')
app.include_router(auth_router, prefix='/auth')

uvicorn.run(app, host="192.168.0.100", port=5000)
