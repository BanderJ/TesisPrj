from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import os

# Configurar Jinja2Templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

app = APIRouter()

@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

