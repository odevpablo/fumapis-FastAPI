from sqlalchemy.orm import Session
from sqlalchemy import or_
from .. import models
from ..schemas.cidadao import CidadaoCreate, CidadaoUpdate
from typing import List, Optional, Any, Union, Dict

def clean_null_values(cidadao: Any) -> None:
    """
    Converte strings 'NULL' para None em um objeto cidadão.
    """
    if cidadao is None:
        return
        
    fields_to_clean = [
        'cpf', 'cpf_conjuge', 'telefone', 'email', 
        'nome_conjuge', 'programa_social'
    ]
    
    for field in fields_to_clean:
        if hasattr(cidadao, field):
            value = getattr(cidadao, field)
            if isinstance(value, str) and value.upper() == 'NULL':
                setattr(cidadao, field, None)

def get_cidadao(db: Session, cidadao_id: int):
    """
    Retorna um cidadão pelo ID.
    """
    cidadao = db.query(models.Cidadao).filter(models.Cidadao.id == cidadao_id).first()
    clean_null_values(cidadao)
    return cidadao

def get_cidadao_by_cpf(db: Session, cpf: str):
    """
    Retorna um cidadão pelo CPF.
    """
    cidadao = db.query(models.Cidadao).filter(models.Cidadao.cpf == cpf).first()
    clean_null_values(cidadao)
    return cidadao

def get_cidadaos(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    bairro: Optional[str] = None,
    status_cadastro: Optional[str] = None,
    ativo: Optional[bool] = None,
    elegivel: Optional[bool] = None
):
    """
    Retorna uma lista de cidadãos com filtros opcionais.
    """
    query = db.query(models.Cidadao)
    
    # Aplicar filtros se fornecidos
    if bairro:
        query = query.filter(models.Cidadao.bairro.ilike(f"%{bairro}%"))
    if status_cadastro:
        query = query.filter(models.Cidadao.status_cadastro == status_cadastro)
    if ativo is not None:
        query = query.filter(models.Cidadao.ativo == ativo)
    if elegivel is not None:
        query = query.filter(models.Cidadao.elegivel == elegivel)
    
    cidadaos = query.offset(skip).limit(limit).all()
    # Limpar valores 'NULL' em cada cidadão retornado
    for cidadao in cidadaos:
        clean_null_values(cidadao)
    return cidadaos

# Função dedicada para buscar por elegibilidade

def get_cidadaos_por_elegibilidade(db: Session, elegivel: bool, skip: int = 0, limit: int = 100):
    """
    Retorna uma lista de cidadãos filtrando por elegibilidade.
    """
    cidadaos = db.query(models.Cidadao).filter(
        models.Cidadao.elegivel == elegivel
    ).offset(skip).limit(limit).all()
    # Limpar valores 'NULL' em cada cidadão retornado
    for cidadao in cidadaos:
        clean_null_values(cidadao)
    return cidadaos

def count_cidadaos(
    db: Session,
    bairro: Optional[str] = None,
    status_cadastro: Optional[str] = None,
    ativo: Optional[bool] = None
) -> int:
    """
    Retorna o número total de cidadãos com filtros opcionais.
    """
    query = db.query(models.Cidadao)
    
    # Aplicar filtros se fornecidos
    if bairro:
        query = query.filter(models.Cidadao.bairro.ilike(f"%{bairro}%"))
    if status_cadastro:
        query = query.filter(models.Cidadao.status_cadastro == status_cadastro)
    if ativo is not None:
        query = query.filter(models.Cidadao.ativo == ativo)
    
    return query.count()

def create_cidadao(db: Session, cidadao: CidadaoCreate):
    """
    Cria um novo cidadão no banco de dados.
    """
    db_cidadao = models.Cidadao(
        nome_completo=cidadao.nome_completo,
        cpf=cidadao.cpf,
        nome_conjuge=cidadao.nome_conjuge,
        cpf_conjuge=cidadao.cpf_conjuge,
        bairro=cidadao.bairro,
        zona=cidadao.zona,
        telefone=cidadao.telefone,
        email=cidadao.email,
        endereco_completo=cidadao.endereco_completo,
        programa_social=cidadao.programa_social,
        status_cadastro=cidadao.status_cadastro or "Ativo",
        ativo=True
    )
    
    db.add(db_cidadao)
    db.commit()
    db.refresh(db_cidadao)
    return db_cidadao

def update_cidadao(db: Session, db_cidadao: models.Cidadao, cidadao: CidadaoUpdate):
    """
    Atualiza os dados de um cidadão existente.
    """
    update_data = cidadao.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_cidadao, field, value)
    
    db.add(db_cidadao)
    db.commit()
    db.refresh(db_cidadao)
    return db_cidadao

def delete_cidadao(db: Session, cidadao_id: int):
    """
    Remove um cidadão do banco de dados (exclusão lógica).
    """
    db_cidadao = get_cidadao(db, cidadao_id)
    if db_cidadao:
        db_cidadao.ativo = False
        db.commit()
        db.refresh(db_cidadao)
    return db_cidadao

def atualizar_votou(db: Session, cidadao_id: int, votou: bool):
    """
    Atualiza o campo votou de um cidadão pelo ID.
    """
    db_cidadao = get_cidadao(db, cidadao_id)
    if db_cidadao is None:
        return None
    db_cidadao.votou = votou
    db.commit()
    db.refresh(db_cidadao)
    return db_cidadao

def atualizar_elegivel(db: Session, cidadao_id: int, elegivel: bool):
    """
    Atualiza o campo elegivel de um cidadão pelo ID.
    """
    db_cidadao = get_cidadao(db, cidadao_id)
    if db_cidadao is None:
        return None
    db_cidadao.elegivel = elegivel
    db.commit()
    db.refresh(db_cidadao)
    return db_cidadao

def search_cidadaos(db: Session, search_term: str, limit: int = 10):
    """
    Busca cidadãos por nome, CPF, bairro ou endereço.
    """
    search = f"%{search_term}%"
    cidadaos = db.query(models.Cidadao).filter(
        or_(
            models.Cidadao.nome_completo.ilike(search),
            models.Cidadao.cpf.ilike(search),
            models.Cidadao.bairro.ilike(search),
            models.Cidadao.endereco_completo.ilike(search)
        )
    ).limit(limit).all()
    # Limpar valores 'NULL' em cada cidadão retornado
    for cidadao in cidadaos:
        clean_null_values(cidadao)
    return cidadaos
