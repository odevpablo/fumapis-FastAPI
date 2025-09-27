from sqlalchemy import Column, Integer, String, Boolean, Date
from datetime import datetime
from .base import Base

class Cidadao(Base):
    __tablename__ = "cidadaos"

    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String(100), nullable=False)
    cpf = Column(String(11), unique=True, index=True, nullable=False)
    nome_conjuge = Column(String(100), nullable=True)
    cpf_conjuge = Column(String(11), nullable=True)
    bairro = Column(String(100), nullable=False)
    zona = Column(String(50), nullable=True)
    telefone = Column(String(15), nullable=True)
    email = Column(String(100), nullable=True)
    endereco_completo = Column(String(200), nullable=False)
    programa_social = Column(String(100), nullable=True)
    status_cadastro = Column(String(50), nullable=False, default="Ativo")
    data_cadastro = Column(Date, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)
    votou = Column(Boolean, default=False)
    elegivel = Column(Boolean, default=True)

