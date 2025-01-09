from fastapi import FastAPI

from . import endpoints as api

def init(app: FastAPI):

    app.include_router(api.ansible_router, prefix="/api")



