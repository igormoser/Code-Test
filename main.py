#region ~~~~~~~~~~~~~~~~~~~ Start do FastAPI (-Imports-) ~~~~~~~~~~~~~~~~~~~ #

import os
import secrets
import redis.asyncio as redis
import json
from celery_app import celery_app
from celery.result import AsyncResult
from tasks import fatorial, somar
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

#endregion

#region ~~~~~~~~~~~~~~~~~~~ Database ( SQLite / SQLAlchemy ~~~~~~~~~~~~~~~~~~~ #

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

CACHE_PREFIX_LIVROS = "livros:"
CACHE_TTL_SECONDS = 300

async def salvar_redis(resposta: dict, *, cache_key: str, ttl: int = CACHE_TTL_SECONDS) -> None:
    await redis_client.setex(cache_key, ttl, json.dumps(resposta, ensure_ascii=False))

async def deletar_redis() -> int:
    chaves = await redis_client.keys("livros:*")
    if not chaves:
        return 0
    return await redis_client.delete(*chaves)

#endregion

#region ~~~~~~~~~~~~~~~~~~~ Session (-Dependency-) ~~~~~~~~~~~~~~~~~~~ #

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#endregion

#region ~~~~~~~~~~~~~~~~~~~ FastAPI (-Docs-) ~~~~~~~~~~~~~~~~~~~ #
app = FastAPI(
    title="Biblioteca",
    description="API de Biblioteca",
    version="1.0.0",
    contact= {"name": "Igor", "email": "igormoser@outlook.com"}
)
#endregion

#region ~~~~~~~~~~~~~~~~~~~ Security (-HTTP Basic-) ~~~~~~~~~~~~~~~~~~~ #

LOGIN = os.getenv("LOGIN", "")
PASSWORD = os.getenv("PASSWORD", "")

security = HTTPBasic()

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    login_correct = secrets.compare_digest(credentials.username, LOGIN)
    password_correct = secrets.compare_digest(credentials.password, PASSWORD)

    if not (login_correct and password_correct):
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas.",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
#endregion

#region ~~~~~~~~~~~~~~~~~~~ ORM Models ~~~~~~~~~~~~~~~~~~~ #

class Livro(Base):
    __tablename__ = "livros"
    id = Column(Integer, primary_key=True)
    titulo = Column(String, index=True)
    autor = Column(String, index=True)
    ano = Column(Integer)

Base.metadata.create_all(bind=engine)

#endregion

#region ~~~~~~~~~~~~~~~~~~~ Schemas (-Pydantic-) ~~~~~~~~~~~~~~~~~~~ #

class CriarLivro(BaseModel):
    titulo: str
    autor: str
    ano: int

class AtualizarLivro(BaseModel):
    titulo: str
    autor: str
    ano: int

class SomaRequest(BaseModel):
    a: int
    b: int

class FatorialRequest(BaseModel):
    n: int

#endregion

#region ~~~~~~~~~~~~~~~~~~~ EndPoints ~~~~~~~~~~~~~~~~~~~ #

@app.get("/debug/redis")
async def debug_redis():
    chaves = await redis_client.keys("livros:*")
    livros = []

    for chave in chaves:
        valor = await redis_client.get(chave)
        ttl = await redis_client.ttl(chave)

        livros.append({"chave": chave, "valor": json.loads(valor) if valor else None, "ttl": ttl})

    return livros

@app.post("/tarefas/soma", dependencies=[Depends(authenticate_user)])
def post_tarefa_soma(payload: SomaRequest):
    task = somar.delay(payload.a, payload.b)

    return {
        "mensagem": "Tarefa de soma enviada com sucesso.",
        "task_id": task.id,
        "status": "PENDING",
        "operacao": "soma",
        "entrada": {
            "a": payload.a,
            "b": payload.b,
        },
    }


@app.post("/tarefas/fatorial", dependencies=[Depends(authenticate_user)])
def post_tarefa_fatorial(payload: FatorialRequest):
    task = fatorial.delay(payload.n)

    return {
        "mensagem": "Tarefa de fatorial enviada com sucesso.",
        "task_id": task.id,
        "status": "PENDING",
        "operacao": "fatorial",
        "entrada": {
            "n": payload.n,
        },
    }

@app.get("/tarefas/{task_id}", dependencies=[Depends(authenticate_user)])
def get_status_tarefa(task_id: str):
    task = AsyncResult(task_id, app=celery_app)

    resposta = {
        "task_id": task.id,
        "status": task.status,
    }

    if task.status == "PENDING":
        resposta["mensagem"] = "Tarefa aguardando processamento."
    elif task.status == "STARTED":
        resposta["mensagem"] = "Tarefa em processamento."
    elif task.status == "SUCCESS":
        resposta["mensagem"] = "Tarefa concluída com sucesso."
        resposta["resultado"] = task.result
    elif task.status == "FAILURE":
        resposta["mensagem"] = "Tarefa falhou."
        resposta["erro"] = str(task.result)
    else:
        resposta["mensagem"] = "Status da tarefa obtido com sucesso."

    return resposta

@app.get("/livros", dependencies=[Depends(authenticate_user)])
async def get_livros(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):

    cache_key = f"livros:skip={skip}&limit={limit}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    total = db.query(Livro).count()

    livros_db = (
        db.query(Livro)
        .order_by(Livro.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    livros_paginados = [
        {"id": livro.id, "titulo": livro.titulo, "autor": livro.autor, "ano": livro.ano}
        for livro in livros_db
    ]

    mensagem = "Biblioteca vazia!" if total == 0 else "Livros cadastrados."

    resposta = {
        "mensagem": mensagem,
        "livros": livros_paginados,
        "total": total,
        "skip": skip,
        "limit": limit
    }

    await salvar_redis(resposta, cache_key=cache_key)

    return resposta

#endregion

#region ~~~~~~~~~~~~~~~~~~~ CRUD ~~~~~~~~~~~~~~~~~~~ #

@app.get("/livros/{id_livro}", dependencies=[Depends(authenticate_user)])
def get_livro(id_livro: int, db: Session = Depends(get_db)):
    livro_db = db.query(Livro).filter(Livro.id == id_livro).first()

    if livro_db is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    return {
        "id": livro_db.id,
        "titulo": livro_db.titulo,
        "autor": livro_db.autor,
        "ano": livro_db.ano,
    }

@app.post("/livros", dependencies=[Depends(authenticate_user)])
async def post_livros(livro: CriarLivro, db: Session = Depends(get_db)):
    novo_livro = Livro(
        titulo=livro.titulo,
        autor=livro.autor,
        ano=livro.ano,
    )
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)

    await deletar_redis()

    return {
        "mensagem": "Livro criado com sucesso!",
        "livro": {
            "id": novo_livro.id,
            "titulo": novo_livro.titulo,
            "autor": novo_livro.autor,
            "ano": novo_livro.ano,
        },
    }

@app.put("/livros/{id_livro}", dependencies=[Depends(authenticate_user)])
async def put_livro(id_livro: int, livro: AtualizarLivro, db: Session = Depends(get_db)):

    livro_db = db.query(Livro).filter(Livro.id == id_livro).first()

    if livro_db is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    livro_db.titulo = livro.titulo
    livro_db.autor = livro.autor
    livro_db.ano = livro.ano

    db.commit()
    db.refresh(livro_db)

    await deletar_redis()

    return {
        "mensagem": "Livro atualizado com sucesso!",
        "livro": {
            "id": livro_db.id,
            "titulo": livro_db.titulo,
            "autor": livro_db.autor,
            "ano": livro_db.ano,
        },
    }

@app.delete("/livros/{id_livro}", dependencies=[Depends(authenticate_user)])
async def delete_livro(id_livro: int, db: Session = Depends(get_db)):
    livro_db = db.query(Livro).filter(Livro.id == id_livro).first()

    if livro_db is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    livro_removido = {
        "id": livro_db.id,
        "titulo": livro_db.titulo,
        "autor": livro_db.autor,
        "ano": livro_db.ano,
    }

    db.delete(livro_db)
    db.commit()

    await deletar_redis()

    return {
        "mensagem": "Livro deletado com sucesso!",
        "livro": livro_removido,
    }
#endregion
