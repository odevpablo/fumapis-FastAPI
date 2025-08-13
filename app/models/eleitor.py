from sqlalchemy import Column, Integer, String, Date, Boolean
from .base import Base
from datetime import date

class Eleitor(Base):
    __tablename__ = "eleitores"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(11), unique=True, nullable=False)
    titulo_eleitor = Column(String(12), unique=True, nullable=False)
    zona_eleitoral = Column(String(10))
    secao_eleitoral = Column(String(10))
    endereco = Column(String(200))
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(String(2))
    telefone = Column(String(15))
    email = Column(String(100))
    data_nascimento = Column(Date)
    data_cadastro = Column(Date, default=date.today)
    ativo = Column(Boolean, default=True)