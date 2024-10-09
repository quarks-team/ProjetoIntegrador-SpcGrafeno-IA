from fastapi import FastAPI
from app.controllers import item_controller  # Supondo que este seja seu controller

app = FastAPI(
    title="Projeto Integrador API",
    description="API para o Projeto Integrador SPC Grafeno - IA",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Items",
            "description": "Operações relacionadas a items"
        },
        # Você pode adicionar mais tags aqui para categorizar endpoints
    ]
)

# Inclui rotas dos controllers
app.include_router(item_controller.router)

@app.get("/", tags=["Healthcheck"])
async def read_root():
    return {"message": "API is running!"}
