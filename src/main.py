from fastapi import FastAPI, Request, status, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import WebSocket
from src.routes.auth_login import auth as auth_router
from src.routes.cafiultor import caficultor_router
from src.routes.tipo_documento import tipo_documento_router
from src.utilities.jwt_utils import verificar_token
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Esto permite que el navegador encuentre el archivo generado automáticamente
app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.mount("/resources", StaticFiles(directory="src/resources"), name="resources")

# Configurar Jinja2Templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

# ==================== SISTEMA DE AUTENTICACIÓN (Dependencias) ====================

class RequerirLoginException(Exception):
    """Excepción para manejar redirecciones a login desde dependencias"""
    pass

@app.exception_handler(RequerirLoginException)
async def auth_exception_handler(request: Request, exc: RequerirLoginException):
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)

def obtener_usuario_actual(request: Request):
    """
    Dependencia que sustituye al @jwt_token_requerido de Flask.
    Si el usuario no está logueado, interrumpe y redirige al login automáticamente.
    """
    token = request.cookies.get("access_token")
    if not token or not token.startswith("Bearer "):
        raise RequerirLoginException()
    
    token = token.split(" ")[1]
    user = verificar_token(token)
    
    if not user:
        raise RequerirLoginException()
    
    return user

# ==================== RUTAS ====================

### Include the auth router to handle authentication-related routes
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(caficultor_router, prefix="/caficultor", tags=["caficultor"])
app.include_router(tipo_documento_router, prefix="/tipo-documento", tags=["tipo-documento"])

@app.get("/")
@app.get("/inicio")
async def inicio(request: Request, user: dict = Depends(obtener_usuario_actual)):
    """
    Página de inicio del sistema
    """
    return templates.TemplateResponse("inicio.html", {"request": request, "user": user})

@app.get("/registro")
async def registro(request: Request, user: dict = Depends(obtener_usuario_actual)):
    """
    Página de registro de muestras
    """
    return templates.TemplateResponse("registro.html", {"request": request, "user": user})



### startup to send a message to the console when the application starts
@app.on_event("startup")
async def startup_event():
    print("Application has started successfully!")

### shutdown to send a message to the console when the application is shutting down
@app.on_event("shutdown")
async def shutdown_event():
    print("Application is shutting down...")
