# API Biblioteca - FastAPI + SQLite + Redis + Celery + Kafka + Kubernetes

Projeto desenvolvido no contexto do curso **Back-End Python EBAC**, com foco em uma API de biblioteca construída com **FastAPI**, persistência em **SQLite/SQLAlchemy**, autenticação **HTTP Basic**, cache com **Redis**, tarefas assíncronas com **Celery** e apoio de infraestrutura com **Docker/Podman**, **Kafka** e **Kubernetes**.

## Visão geral

A aplicação expõe um CRUD de livros com autenticação, paginação e invalidação de cache. Além disso, possui endpoints para envio e acompanhamento de tarefas assíncronas de soma e fatorial.

## Funcionalidades principais

- CRUD completo de livros
- Paginação no endpoint de listagem
- Autenticação HTTP Basic
- Cache de listagem com Redis
- Invalidação de cache ao criar, atualizar e remover livros
- Tarefas assíncronas com Celery
- Consulta de status das tarefas
- Ambiente Kafka com ZooKeeper e Kafka UI
- Manifestos Kubernetes para deploy da API
- Testes com pytest

## Tecnologias utilizadas

- Python 3.14
- FastAPI
- SQLAlchemy
- SQLite
- Redis
- Celery
- Poetry
- Pytest / pytest-cov
- Docker / Podman
- Kafka / ZooKeeper / Kafka UI
- Kubernetes

## Estrutura básica do projeto

```text
.
├── main.py
├── celery_app.py
├── tasks.py
├── pokemon.py
├── test_auth.py
├── test_tasks.py
├── test_pokemon.py
├── test_pokemon_fixture.py
├── pyproject.toml
├── poetry.lock
├── Dockerfile
├── docker-compose.yml
├── deployment.yaml
├── service.yaml
└── README.md
```

## Endpoints principais

### Livros

- `GET /livros` — lista livros com paginação (`skip` e `limit`)
- `GET /livros/{id_livro}` — busca um livro por ID
- `POST /livros` — cria um novo livro
- `PUT /livros/{id_livro}` — atualiza um livro
- `DELETE /livros/{id_livro}` — remove um livro

### Redis

- `GET /debug/redis` — mostra chaves, valores e TTL do cache de livros

### Tarefas assíncronas

- `POST /tarefas/soma` — envia uma tarefa de soma
- `POST /tarefas/fatorial` — envia uma tarefa de fatorial
- `GET /tarefas/{task_id}` — consulta o status de uma tarefa

## Variáveis de ambiente

A aplicação utiliza variáveis de ambiente para banco de dados, autenticação e Redis.

### Exemplo

```env
DATABASE_URL=sqlite:///./biblioteca.db
LOGIN=admin
PASSWORD=admin
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379/0
```

### Observação importante

O arquivo `main.py` usa `REDIS_HOST=localhost` por padrão, enquanto `celery_app.py` usa `REDIS_HOST=redis` por padrão. Ao rodar tudo localmente fora de containers, vale a pena definir essas variáveis explicitamente para evitar inconsistências.

## Instalação com Poetry

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
```

### 2. Instalar as dependências

```bash
poetry install
```

### 3. Definir as variáveis de ambiente

No PowerShell:

```powershell
$env:DATABASE_URL="sqlite:///./biblioteca.db"
$env:LOGIN="admin"
$env:PASSWORD="admin"
$env:REDIS_HOST="localhost"
$env:REDIS_PORT="6379"
$env:REDIS_URL="redis://localhost:6379/0"
```

### 4. Subir um Redis local

Exemplo com Docker:

```bash
docker run -d --name redis -p 6379:6379 redis:7
```

ou com Podman:

```bash
podman run -d --name redis -p 6379:6379 docker.io/library/redis:7
```

### 5. Rodar a API

```bash
poetry run uvicorn main:app --reload
```

A documentação interativa ficará disponível em:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Executando o worker do Celery

Com o Redis em execução e as variáveis configuradas:

```bash
poetry run celery -A celery_app.celery_app worker --loglevel=info
```

## Executando com Docker

O projeto possui um `Dockerfile` para empacotar a aplicação FastAPI com Poetry.

### Build da imagem

```bash
docker build -t fastapi-app .
```

ou com Podman:

```bash
podman build -t localhost/fastapi-app:latest .
```

### Rodando o container

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL="sqlite:///./biblioteca.db" \
  -e LOGIN="admin" \
  -e PASSWORD="admin" \
  fastapi-app
```

> Para usar cache Redis e tarefas Celery dentro de containers, lembre-se de disponibilizar também um Redis acessível pela aplicação.

## Ambiente Kafka

O arquivo `docker-compose.yml` deste projeto sobe um ambiente local com:

- ZooKeeper
- Kafka
- Kafka UI

### Subir o ambiente

Com Docker:

```bash
docker compose up -d --build
```

Com Podman:

```bash
podman compose up -d --build
```

### Acessos esperados

- Kafka: `localhost:9092`
- ZooKeeper: `localhost:2181`
- Kafka UI: `http://localhost:8080`

### Derrubar o ambiente

```bash
docker compose down
```

ou

```bash
podman compose down
```

## Kubernetes

O projeto contém manifestos para deploy da API no Kubernetes.

### Arquivos

- `deployment.yaml`
- `service.yaml`

### O que está definido

- Deployment com **2 réplicas**
- Imagem `localhost/fastapi-app:latest`
- Porta do container: `8000`
- Service do tipo `ClusterIP`

### Aplicando os manifestos

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### Verificando os recursos

```bash
kubectl get deployments
kubectl get pods
kubectl get services
```

> Antes de aplicar no cluster, a imagem `localhost/fastapi-app:latest` precisa estar disponível para o ambiente Kubernetes utilizado.

## Testes

O projeto possui testes automatizados com `pytest`.

### Rodar todos os testes

```bash
poetry run pytest
```

### Cobertura prevista nos arquivos atuais

- `test_auth.py` — autenticação da API
- `test_tasks.py` — tarefas de soma e fatorial
- `test_pokemon.py` — testes básicos de funções auxiliares
- `test_pokemon_fixture.py` — testes usando fixtures

## Exemplos de uso da API

### Autenticação

Os endpoints protegidos usam **HTTP Basic**.

Exemplo no header:

```text
Authorization: Basic <token_base64>
```

### Exemplo de criação de livro

```json
{
  "titulo": "Dom Casmurro",
  "autor": "Machado de Assis",
  "ano": 1899
}
```

### Exemplo de envio de tarefa de soma

```json
{
  "a": 10,
  "b": 5
}
```

### Exemplo de envio de tarefa de fatorial

```json
{
  "n": 5
}
```

## Observações

- O banco de dados utilizado é SQLite.
- A listagem de livros usa cache com TTL de 300 segundos.
- As tarefas Celery simulam processamento com `sleep(3)`.
- O repositório já inclui um README anterior focado apenas no ambiente Kafka; este documento expande a documentação para o projeto como um todo.
- O arquivo `test_auth.db` é usado em testes e não deve ser tratado como artefato principal da aplicação.

## Autor

**Igor Moser**  
Projeto acadêmico do curso **Back-End Python EBAC**.
