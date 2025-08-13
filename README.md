# FastAPI Boilerplate

## Como rodar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure o acesso ao banco PostgreSQL em `app/database.py`:
   ```python
   DATABASE_URL = "postgresql://usuario:senha@localhost:5432/fumapis"
   ```
   Troque `usuario` e `senha` pelos seus dados.

3. Rode o servidor:
   ```bash
   uvicorn main:app --reload
   ```

## Rotas de usuário
- POST `/users` — cadastra novo usuário
- GET `/users` — lista todos os usuários

Acesse http://localhost:8000/docs para testar as rotas interativamente.

