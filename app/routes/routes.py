import os
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Path as PathParam
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.user import UserDB, UserCreate, UserOut, UserInDB, hash_password
from app.schemas.cidadao import Cidadao, CidadaoCreate, CidadaoUpdate
from app.crud import cidadao as crud_cidadao
from app.schemas.cidadao import Cidadao, CidadaoInDB
from passlib.hash import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.responses import FileResponse, JSONResponse
from fastapi import Request, Response
import xml.etree.ElementTree as ET
from fastapi.responses import Response as FastAPIResponse

SECRET_KEY = "PMTUZQX7@"  # Troque por uma chave forte
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    import bcrypt
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"Erro ao verificar senha: {e}")
        return False

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_name(db: Session, username: str):
    return db.query(UserDB).filter(UserDB.name == username).first()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_name(db, username)
    if user is None:
        raise credentials_exception
    return user

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Tenta executar uma consulta simples para verificar a conexão
        db.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "database": "connection failed", "error": str(e)}
        )


import os
from pathlib import Path

# Obtém o diretório absoluto do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

# Cria o diretório de uploads se não existir
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    print(f"Pasta de uploads criada em: {UPLOAD_FOLDER}")
    print(f"Diretório atual: {os.getcwd()}")
    print(f"Conteúdo do diretório: {os.listdir(BASE_DIR)}")
except Exception as e:
    print(f"Erro ao criar pasta de uploads: {e}")
    raise

@router.get("/arquivos")
async def listar_arquivos():
    """Lista todos os arquivos enviados"""
    try:
        if not os.path.exists(UPLOAD_FOLDER):
            return {"arquivos": []}
            
        arquivos = []
        for nome_arquivo in os.listdir(UPLOAD_FOLDER):
            caminho = os.path.join(UPLOAD_FOLDER, nome_arquivo)
            if os.path.isfile(caminho):
                arquivos.append({
                    "nome": nome_arquivo,
                    "tamanho_kb": round(os.path.getsize(caminho) / 1024, 2),
                    "data_modificacao": os.path.getmtime(caminho)
                })
        
        # Ordena por data de modificação (mais recente primeiro)
        arquivos.sort(key=lambda x: x["data_modificacao"], reverse=True)
        
        return {"arquivos": arquivos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar arquivos: {str(e)}")

@router.get("/arquivos/{nome_arquivo}")
async def visualizar_arquivo(
    nome_arquivo: str = PathParam(..., description="Nome do arquivo a ser visualizado ou baixado"),
    download: bool = Query(False, description="Se True, faz download do arquivo em vez de mostrar o conteúdo")
):
    """Visualiza ou baixa um arquivo específico"""
    try:
        # Previne path traversal
        if '..' in nome_arquivo or '/' in nome_arquivo or '\\' in nome_arquivo:
            raise HTTPException(status_code=400, detail="Nome de arquivo inválido")
            
        caminho_arquivo = os.path.join(UPLOAD_FOLDER, nome_arquivo)
        
        if not os.path.isfile(caminho_arquivo):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        # Se for para baixar o arquivo
        if download:
            return FileResponse(
                path=caminho_arquivo,
                filename=nome_arquivo,
                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        # Se for para visualizar o conteúdo
        if nome_arquivo.lower().endswith(('.xlsx', '.xls')):
            try:
                df = pd.read_excel(caminho_arquivo, engine='openpyxl')
                
                # Converte para dicionário e limpa os dados
                def clean_data(data):
                    if isinstance(data, dict):
                        return {k: clean_data(v) for k, v in data.items()}
                    elif isinstance(data, list):
                        return [clean_data(item) for item in data]
                    elif pd.isna(data):
                        return None
                    return data
                
                # Pega as primeiras 50 linhas para visualização
                dados = df.head(50).fillna('').to_dict(orient='records')
                dados_limpos = clean_data(dados)
                
                return {
                    "nome_arquivo": nome_arquivo,
                    "tamanho_kb": round(os.path.getsize(caminho_arquivo) / 1024, 2),
                    "total_linhas": len(df),
                    "colunas": df.columns.tolist(),
                    "dados": dados_limpos,
                    "mensagem": f"Mostrando 50 primeiras linhas de {len(df)}" if len(df) > 50 else "Mostrando todas as linhas"
                }
                
            except Exception as e:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Não foi possível ler o arquivo Excel: {str(e)}"
                )
        else:
            # Para outros tipos de arquivo, retorna informações básicas
            with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                conteudo = f.read(1000)  # Lê apenas os primeiros 1000 caracteres
                
            return {
                "nome_arquivo": nome_arquivo,
                "tipo": "texto",
                "tamanho_kb": round(os.path.getsize(caminho_arquivo) / 1024, 2),
                "preview": conteudo,
                "mensagem": "Mostrando os primeiros 1000 caracteres"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")

@router.post("/upload-xlsx")
async def upload_xlsx(file: UploadFile = File(...)):
    print(f"Iniciando upload do arquivo: {file.filename}")
    print(f"Pasta de upload: {UPLOAD_FOLDER}")
    print(f"Diretório atual: {os.getcwd()}")
    
    try:
        # Verifica se o arquivo é XLSX
        if not file.filename or not file.filename.lower().endswith(('.xlsx', '.xls')):
            error_msg = f"Formato de arquivo inválido: {file.filename}. Apenas XLSX/XLS são aceitos"
            print(error_msg)
            return JSONResponse(
                status_code=400,
                content={"message": error_msg}
            )
        
        # Garante que o diretório de upload existe
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        print(f"Conteúdo da pasta de upload: {os.listdir(UPLOAD_FOLDER)}")
        
        # Cria um nome de arquivo seguro
        import uuid
        import re
        
        # Remove caracteres não seguros do nome do arquivo
        safe_filename = re.sub(r'[^\w\-_. ]', '_', file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        
        # Se o arquivo já existir, adiciona um sufixo único
        counter = 1
        while os.path.exists(file_path):
            name, ext = os.path.splitext(safe_filename)
            file_path = os.path.join(UPLOAD_FOLDER, f"{name}_{counter}{ext}")
            counter += 1
        
        print(f"Salvando arquivo em: {file_path}")
        
        try:
            # Lê o conteúdo do arquivo
            contents = await file.read()
            if not contents:
                raise ValueError("O arquivo está vazio")
            
            # Garante que o diretório existe
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
            # Salva o arquivo
            with open(file_path, "wb") as buffer:
                buffer.write(contents)
            
            print(f"Arquivo salvo com sucesso. Tamanho: {len(contents)} bytes")
            print(f"Arquivo existe? {os.path.exists(file_path)}")
            print(f"Caminho absoluto: {os.path.abspath(file_path)}")
            
            # Verifica se o arquivo foi realmente salvo
            if not os.path.exists(file_path):
                raise Exception(f"Falha ao salvar o arquivo em {file_path}")
            
            # Tenta ler o arquivo XLSX
            print("Lendo arquivo XLSX...")
            df = pd.read_excel(file_path, engine='openpyxl')
            
            if df.empty:
                print("Aviso: O arquivo Excel está vazio")
                return JSONResponse(
                    status_code=200,
                    content={"message": "Arquivo processado, mas está vazio"}
                )
            
            # Função para converter valores NaN para None
            def clean_data(data):
                if isinstance(data, dict):
                    return {k: clean_data(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [clean_data(item) for item in data]
                elif pd.isna(data):
                    return None
                return data
            
            # Converte para dicionário e limpa os dados
            data = df.to_dict(orient='records')
            data_cleaned = clean_data(data)
            
            # Prepara a resposta
            colunas = df.columns.tolist()
            amostra = df.head().fillna('').to_dict(orient='records')
            amostra_cleaned = clean_data(amostra)
            total_linhas = len(df)
            
            print(f"Arquivo processado com sucesso. Colunas: {colunas}, Total de linhas: {total_linhas}")
            
            response_data = {
                "message": "Arquivo processado com sucesso",
                "nome_arquivo": safe_filename,
                "caminho_salvo": file_path,
                "tamanho_arquivo": f"{os.path.getsize(file_path) / 1024:.2f} KB",
                "colunas": colunas,
                "amostra_dados": amostra_cleaned,
                "total_linhas": total_linhas
            }
            
            # Garante que não há valores NaN na resposta
            import json
            json.dumps(response_data, default=str)  # Testa a serialização
            
            return response_data
            
        except Exception as e:
            error_msg = f"Erro ao processar o arquivo: {str(e)}"
            print(error_msg)
            return JSONResponse(
                status_code=500,
                content={"message": error_msg}
            )
            
    except Exception as e:
        error_msg = f"Erro inesperado: {str(e)}"
        print(error_msg)
        return JSONResponse(
            status_code=500,
            content={"message": error_msg}
        )

@router.post("/users", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(UserDB).filter(UserDB.name == user.name).first():
        raise HTTPException(status_code=400, detail="Usuário já existe")
    novo_usuario = UserDB(name=user.name, password=hash_password(user.password))
    db.add(novo_usuario)
    try:
        db.commit()
        db.refresh(novo_usuario)
        return novo_usuario
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro ao criar usuário (possível duplicidade)")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/users", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(UserDB).all()

# Rota de login
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(f"Tentativa de login para o usuário: {form_data.username}")
    user = get_user_by_name(db, form_data.username)
    print(f"Usuário encontrado: {user is not None}")
    
    if not user:
        print("Usuário não encontrado")
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
        
    print(f"Verificando senha para o usuário: {user.name}")
    if not verify_password(form_data.password, user.password):
        print("Senha incorreta")
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
        
    print("Credenciais válidas, gerando token...")
    access_token = create_access_token(data={"sub": user.name})
    return {"access_token": access_token, "token_type": "bearer"}

# Exemplo de rota protegida
@router.get("/me", response_model=UserOut)
def read_users_me(current_user: UserDB = Depends(get_current_user)):
    return current_user

# Rota GET que retorna todas as tabelas e colunas do banco de dados em formato XML
@router.get("/estrutura-bd", response_class=FastAPIResponse)
async def obter_estrutura_bd(db: Session = Depends(get_db)):
    try:
        from sqlalchemy import inspect
        
        # Cria o elemento raiz do XML
        root = ET.Element("banco_de_dados")
        
        # Obtém o inspetor do banco de dados
        inspector = inspect(db.get_bind())
        
        # Obtém todas as tabelas do banco de dados
        tabelas = inspector.get_table_names()
        
        for nome_tabela in tabelas:
            # Cria um elemento para cada tabela
            tabela_element = ET.SubElement(root, "tabela", nome=nome_tabela)
            
            # Obtém as colunas da tabela atual
            colunas = inspector.get_columns(nome_tabela)
            
            # Adiciona informações sobre cada coluna
            for coluna in colunas:
                coluna_element = ET.SubElement(tabela_element, "coluna")
                ET.SubElement(coluna_element, "nome").text = coluna['name']
                ET.SubElement(coluna_element, "tipo").text = str(coluna['type'])
                ET.SubElement(coluna_element, "nulo").text = "SIM" if coluna['nullable'] else "NÃO"
                if coluna.get('primary_key'):
                    ET.SubElement(coluna_element, "chave_primaria").text = "SIM"
        
        # Converte para string XML
        xml_string = ET.tostring(root, encoding="unicode", method="xml")
        
        # Formata o XML com recuos para melhor legibilidade
        from xml.dom import minidom
        xml_pretty = minidom.parseString(xml_string).toprettyxml(indent="  ")
        
        # Retorna a resposta com o tipo de conteúdo correto
        return FastAPIResponse(
            content=xml_pretty,
            media_type="application/xml",
            status_code=200
        )
        
    except Exception as e:
        return Response(
            content=f"<erro>Erro ao obter estrutura do banco de dados: {str(e)}</erro>",
            media_type="application/xml",
            status_code=500
        )

# Rotas para gerenciamento de cidadãos
@router.post("/cidadaos/", response_model=CidadaoInDB, status_code=status.HTTP_201_CREATED)
def criar_cidadao(
    cidadao: CidadaoCreate,
    db: Session = Depends(get_db)
):
    """
    Cria um novo cidadão no sistema.
    Acesso público - não requer autenticação.
    """
    # Verifica se já existe um cidadão com o mesmo CPF
    db_cidadao = crud_cidadao.get_cidadao_by_cpf(db, cpf=cidadao.cpf)
    if db_cidadao:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um cidadão cadastrado com este CPF"
        )
    
    return crud_cidadao.create_cidadao(db=db, cidadao=cidadao)

@router.get("/cidadaos/", response_model=List[Cidadao])
def listar_cidadaos(
    skip: int = 0,
    limit: int = 100,
    bairro: Optional[str] = None,
    status_cadastro: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista os cidadãos cadastrados com filtros opcionais.
    Acesso público - não requer autenticação.
    """
    return crud_cidadao.get_cidadaos(
        db=db,
        skip=skip,
        limit=limit,
        bairro=bairro,
        status_cadastro=status_cadastro
    )

@router.get("/cidadaos/contar")
def contar_cidadaos(
    bairro: Optional[str] = None,
    status_cadastro: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retorna a contagem total de cidadãos com filtros opcionais.
    Acesso público - não requer autenticação.
    """
    total = crud_cidadao.count_cidadaos(
        db=db,
        bairro=bairro,
        status_cadastro=status_cadastro
    )
    return {"total": total}

@router.get("/cidadaos/{cidadao_id}", response_model=CidadaoInDB)
def obter_cidadao(
    cidadao_id: int = PathParam(gt=0, title="ID do cidadão"),
    db: Session = Depends(get_db)
):
    """
    Obtém os detalhes de um cidadão específico pelo ID.
    Acesso público - não requer autenticação.
    """
    db_cidadao = crud_cidadao.get_cidadao(db, cidadao_id=cidadao_id)
    if db_cidadao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cidadão não encontrado"
        )
    return db_cidadao

@router.get("/cidadaos/cpf/{cpf}", response_model=CidadaoInDB, tags=["Cidadãos"], summary="Buscar cidadão por CPF",
          description="Retorna os dados de um cidadão com base no CPF informado.")
async def buscar_cidadao_por_cpf(
    cpf: str = PathParam(..., min_length=11, max_length=11, pattern=r'^[0-9]{11}$', description="CPF do cidadão (apenas números)"),
    db: Session = Depends(get_db)
):
    """
    Busca um cidadão pelo CPF.
    """
    db_cidadao = crud_cidadao.get_cidadao_by_cpf(db, cpf=cpf)
    if db_cidadao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cidadão com CPF {cpf} não encontrado"
        )
    return db_cidadao

@router.get("/cidadaos/nome/{nome}", response_model=List[CidadaoInDB], tags=["Cidadãos"], summary="Buscar cidadãos por nome", description="Retorna uma lista de cidadãos cujo nome contenha o termo informado.")
async def buscar_cidadaos_por_nome(
    nome: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Busca cidadãos pelo nome (parcial ou completo).
    """
    resultados = crud_cidadao.search_cidadaos(db, search_term=nome, limit=limit)
    if not resultados:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nenhum cidadão encontrado com o nome '{nome}'"
        )
    return resultados

@router.put("/cidadaos/{cidadao_id}", response_model=CidadaoInDB)
def atualizar_cidadao(
    cidadao_id: int,
    cidadao: CidadaoUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Atualiza os dados de um cidadão existente.
    """
    db_cidadao = crud_cidadao.get_cidadao(db, cidadao_id=cidadao_id)
    if db_cidadao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cidadão não encontrado"
        )
    
    # Verifica se o CPF já está em uso por outro cidadão
    if cidadao.cpf:
        cidadao_com_mesmo_cpf = crud_cidadao.get_cidadao_by_cpf(db, cpf=cidadao.cpf)
        if cidadao_com_mesmo_cpf and cidadao_com_mesmo_cpf.id != cidadao_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe outro cidadão com este CPF"
            )
    
    return crud_cidadao.update_cidadao(db=db, db_cidadao=db_cidadao, cidadao=cidadao)

@router.delete("/cidadaos/{cidadao_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_cidadao(
    cidadao_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Remove um cidadão do sistema (exclusão lógica).
    """
    db_cidadao = crud_cidadao.get_cidadao(db, cidadao_id=cidadao_id)
    if db_cidadao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cidadão não encontrado"
        )
    
    crud_cidadao.delete_cidadao(db=db, cidadao_id=cidadao_id)
    return None

from fastapi import Body

@router.get("/cidadaos/elegiveis/{elegivel}", response_model=List[CidadaoInDB], tags=["Cidadãos"], summary="Buscar cidadãos por elegibilidade", description="Retorna cidadãos filtrando pelo campo elegivel (true/false).")
def buscar_cidadaos_por_elegibilidade(
    elegivel: bool,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retorna cidadãos filtrando pelo campo elegivel (true/false).
    """
    return crud_cidadao.get_cidadaos_por_elegibilidade(db, elegivel, skip=skip, limit=limit)

@router.patch("/cidadaos/{cidadao_id}/votou", response_model=CidadaoInDB, tags=["Cidadãos"], summary="Atualizar status de votação", description="Atualiza o campo votou de um cidadão pelo ID.")
def atualizar_status_votou(
    cidadao_id: int,
    votou: bool = Body(..., embed=True, description="Novo valor para o campo votou (true/false)"),
    db: Session = Depends(get_db)
):
    """
    Atualiza o campo votou de um cidadão pelo ID.
    """
    db_cidadao = crud_cidadao.atualizar_votou(db, cidadao_id=cidadao_id, votou=votou)
    if db_cidadao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cidadão não encontrado"
        )
    return db_cidadao

@router.patch("/cidadaos/{cidadao_id}/elegivel", response_model=CidadaoInDB, tags=["Cidadãos"], summary="Atualizar elegibilidade", description="Atualiza o campo elegivel de um cidadão pelo ID.")
def atualizar_status_elegivel(
    cidadao_id: int,
    elegivel: bool = Body(..., embed=True, description="Novo valor para o campo elegivel (true/false)"),
    db: Session = Depends(get_db)
):
    """
    Atualiza o campo elegivel de um cidadão pelo ID.
    """
    db_cidadao = crud_cidadao.atualizar_elegivel(db, cidadao_id=cidadao_id, elegivel=elegivel)
    if db_cidadao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cidadão não encontrado"
        )
    return db_cidadao
