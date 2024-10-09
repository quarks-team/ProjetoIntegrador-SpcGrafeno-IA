import subprocess
import time
import requests

def test_uvicorn_startup():
    # Inicia o servidor FastAPI com uvicorn
    process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Aguarda alguns segundos para garantir que o servidor iniciou
    time.sleep(5)

    try:
        # Verifica se o servidor está respondendo
        response = requests.get("http://127.0.0.1:8000")
        assert response.status_code == 200  # Verifica se o status é 200 (OK)

    finally:
        # Encerra o processo do servidor
        process.terminate()
        process.wait()  # Aguarda o processo terminar
