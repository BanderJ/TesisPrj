from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi import WebSocket
from app.routes.auth_login import app as auth_login
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Esto permite que el navegador encuentre el archivo generado automáticamente
app.mount("/static", StaticFiles(directory="app/static"), name="static")

### ROUTES ###

### Include the auth_login router to handle authentication-related routes
app.include_router(auth_login, prefix="/auth", tags=["auth"])

@app.get("/")
async def root():
    """
    Ruta raíz que redirige a la página de login
    """
    return RedirectResponse(url="/auth/login")

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