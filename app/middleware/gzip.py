from fastapi.middleware.gzip import GZipMiddleware
from fastapi import FastAPI

def add_gzip_middleware(app: FastAPI, minimum_size: int = 1000) -> None:
    app.add_middleware(GZipMiddleware, minimum_size=minimum_size)
