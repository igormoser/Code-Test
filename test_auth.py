import os
import base64

import pytest
from fastapi.testclient import TestClient


os.environ["DATABASE_URL"] = "sqlite:///./test_auth.db"
os.environ["LOGIN"] = "admin"
os.environ["PASSWORD"] = "123456"

import main


@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    async def fake_get(*args, **kwargs):
        return None

    async def fake_salvar_redis(*args, **kwargs):
        return None

    monkeypatch.setattr(main.redis_client, "get", fake_get)
    monkeypatch.setattr(main, "salvar_redis", fake_salvar_redis)


@pytest.fixture
def client():
    return TestClient(main.app)


def gerar_header_basic(usuario: str, senha: str) -> dict:
    token = base64.b64encode(f"{usuario}:{senha}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def test_autenticacao_com_credenciais_corretas(client):
    headers = gerar_header_basic("admin", "123456")

    response = client.get("/livros", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "mensagem" in data
    assert "livros" in data


def test_autenticacao_com_credenciais_incorretas(client):
    headers = gerar_header_basic("usuario_errado", "senha_errada")

    response = client.get("/livros", headers=headers)

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Credenciais inválidas."
    assert response.headers["www-authenticate"] == "Basic"