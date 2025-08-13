from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date, datetime
from typing import Optional

class CidadaoBase(BaseModel):
    nome_completo: str = Field(..., max_length=100)
    cpf: str = Field(..., min_length=11, max_length=11, pattern=r'^[0-9]{11}$')
    nome_conjuge: Optional[str] = Field(None, max_length=100)
    cpf_conjuge: Optional[str] = Field(None, min_length=11, max_length=11, pattern=r'^[0-9]{11}$')
    bairro: str = Field(..., max_length=100)
    telefone: Optional[str] = Field(None, max_length=15, pattern=r'^[0-9]{10,11}$|^$')
    email: Optional[EmailStr] = None
    endereco_completo: str = Field(..., max_length=200)
    programa_social: Optional[str] = Field(None, max_length=100)
    status_cadastro: str = Field(default="Ativo", max_length=50)

    @validator('cpf')
    def cpf_must_be_valid(cls, v):
        # Validação simples de CPF (pode ser aprimorada)
        if not v.isdigit() or len(v) != 11:
            raise ValueError('CPF deve conter 11 dígitos numéricos')
        return v
    
    @validator('cpf_conjuge')
    def cpf_conjuge_must_be_valid(cls, v):
        if v and (not v.isdigit() or len(v) != 11):
            raise ValueError('CPF do cônjuge deve conter 11 dígitos numéricos')
        return v or None

class CidadaoCreate(CidadaoBase):
    pass

class CidadaoUpdate(BaseModel):
    nome_completo: Optional[str] = Field(None, max_length=100)
    cpf: Optional[str] = Field(None, min_length=11, max_length=11, pattern=r'^[0-9]{11}$')
    nome_conjuge: Optional[str] = Field(None, max_length=100)
    cpf_conjuge: Optional[str] = Field(None, min_length=11, max_length=11, pattern=r'^[0-9]{11}$')
    bairro: Optional[str] = Field(None, max_length=100)
    telefone: Optional[str] = Field(None, max_length=15, pattern=r'^[0-9]{10,11}$|^$')
    email: Optional[EmailStr] = None
    endereco_completo: Optional[str] = Field(None, max_length=200)
    programa_social: Optional[str] = Field(None, max_length=100)
    status_cadastro: Optional[str] = Field(None, max_length=50)
    ativo: Optional[bool] = None

from typing import Optional

class CidadaoInDB(CidadaoBase):
    id: int
    data_cadastro: date
    ativo: bool = True
    votou: Optional[bool] = False
    elegivel: Optional[bool] = True

    class Config:
        from_attributes = True

class Cidadao(CidadaoInDB):
    pass
