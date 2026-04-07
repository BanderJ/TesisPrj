from fastapi import FastAPI, Request, status, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import WebSocket
from app.routes.auth_login import auth as auth_router
from app.utilities.jwt_utils import verificar_token
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Esto permite que el navegador encuentre el archivo generado automáticamente
app.mount("/static", StaticFiles(directory="app/static"), name="static")

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

@app.get("/")
async def root(request: Request, user: dict = Depends(obtener_usuario_actual)):
    """
    Ruta raíz que lleva al inicio del sistema
    """
    return templates.TemplateResponse("inicio.html", {"request": request, "user": user})

@app.get("/inicio")
async def inicio(request: Request, user: dict = Depends(obtener_usuario_actual)):
    """
    Página de inicio del sistema
    """
    return templates.TemplateResponse("inicio.html", {"request": request, "user": user})

### Managment of CORS (Cross-Origin Resource Sharing) to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    allow_credentials=True  # Allow cookies and credentials
)

# All requests from any origin will be allowed to access the API
@app.middleware("http")
async def cors_middleware(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

### Example of a POST endpoint that accepts an item and returns it
class Item(BaseModel):
    name: str
    description: str = None
    price: float

@app.post("/items")
async def create_item(item: Item):
    return {"item": item, "name": item.name, "description": item.description, "price": item.price}

### startup to send a message to the console when the application starts
@app.on_event("startup")
async def startup_event():
    print("Application has started successfully!")

### shutdown to send a message to the console when the application is shutting down
@app.on_event("shutdown")
async def shutdown_event():
    print("Application is shutting down...")

### WebSocket endpoint for real-time communication, allowing clients to connect and receive messages
online_clients = []
@app.websocket("/ws/data")
async def websocket_data(websocket: WebSocket):
    await websocket.accept()
    online_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Data recibida: {data}")
            # Broadcast the received data to all connected clients
            for client in online_clients:
                if client != websocket:
                    await client.send_text(f"Data recibida: {data}")
    except Exception as e:
        print(f"Error en WebSocket: {e}")