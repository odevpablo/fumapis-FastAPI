# API Apuração de Votos

## Sobre a API

Esta API foi desenvolvida com FastAPI para gerenciar usuários, cidadãos e eleitores em um sistema de votação. Ela permite o cadastro, consulta e manipulação de dados dessas entidades, integrando-se a um banco de dados PostgreSQL. O objetivo é fornecer uma interface RESTful simples e eficiente para operações como:

- Cadastro e listagem de usuários
- Gerenciamento de cidadãos (CRUD)
- Gerenciamento de eleitores (CRUD)
- Rotas protegidas para operações sensíveis
- Documentação automática acessível via Swagger (em `/docs`)

A API pode ser utilizada para aplicações de votação, controle de acesso ou sistemas que necessitem de gerenciamento de perfis de usuários.

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

Acesse http://localhost:8000/docs para testar as rotas interativamente.

## Documentação Interativa (Swagger)

A API possui documentação automática gerada pelo Swagger, acessível em [http://localhost:8000/docs](http://localhost:8000/docs) quando o servidor está rodando.

Com essa interface, você pode:

- Visualizar todas as rotas disponíveis, métodos e parâmetros esperados
- Testar requisições diretamente pelo navegador, sem precisar de ferramentas externas (como Postman)
- Ver exemplos de respostas e códigos de status
- Explorar a estrutura dos dados de entrada e saída de cada endpoint

O Swagger facilita o desenvolvimento, testes e integração da API, tornando o uso muito mais prático tanto para desenvolvedores quanto para usuários.

