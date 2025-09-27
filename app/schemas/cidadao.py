from pydantic import BaseModel, EmailStr, Field, validator, field_validator, field_serializer
from datetime import date, datetime
from typing import Optional, Any

class CidadaoBase(BaseModel):
    nome_completo: Optional[str] = Field(None, max_length=100)
    cpf: Optional[str] = Field(None)
    nome_conjuge: Optional[str] = Field(None, max_length=100)
    cpf_conjuge: Optional[str] = Field(None)
    bairro: Optional[str] = Field(None, max_length=100)
    zona: Optional[str] = Field(None, max_length=50)
    telefone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    endereco_completo: Optional[str] = Field(None, max_length=200)
    programa_social: Optional[str] = Field(None, max_length=100)
    status_cadastro: Optional[str] = Field("Ativo", max_length=50)

    @field_validator('cpf', mode='before')
    def validate_cpf(cls, v):
        if v is None or v == '':
            return None
        # Remove caracteres não numéricos
        v = ''.join(filter(str.isdigit, str(v)))
        # Se o CPF estiver vazio após remover caracteres não numéricos, retorna None
        if not v:
            return None
        # Apenas aceita CPFs com 11 dígitos, caso contrário retorna None
        return v if len(v) == 11 else None
    
    @field_validator('cpf_conjuge', mode='before')
    def validate_cpf_conjuge(cls, v):
        if v is None or v == '':
            return None
        # Remove caracteres não numéricos
        v = ''.join(filter(str.isdigit, str(v)))
        # Se o CPF do cônjuge estiver vazio após remover caracteres não numéricos, retorna None
        if not v:
            return None
        # Apenas aceita CPFs com 11 dígitos, caso contrário retorna None
        return v if len(v) == 11 else None
    
    @field_validator('telefone', mode='before')
    def validate_telefone(cls, v):
        if v is None or v == '':
            return None
        # Remove caracteres não numéricos
        v = ''.join(filter(str.isdigit, str(v)))
        # Se o telefone estiver vazio após remover caracteres não numéricos, retorna None
        if not v:
            return None
        # Retorna o número de telefone independente do tamanho
        return v
    
    @field_validator('email', mode='before')
    def validate_email(cls, v):
        if v is None or v == '':
            return None
        return v
    
    @field_serializer('cpf', 'cpf_conjuge', 'telefone')
    def serialize_fields(self, value):
        return value if value is not None else None

class CidadaoCreate(CidadaoBase):
    pass

class CidadaoUpdate(BaseModel):
    nome_completo: Optional[str] = Field(None, max_length=100)
    cpf: Optional[str] = Field(None, min_length=11, max_length=11, pattern=r'^[0-9]{11}$')
    nome_conjuge: Optional[str] = Field(None, max_length=100)
    cpf_conjuge: Optional[str] = Field(None, min_length=11, max_length=11, pattern=r'^[0-9]{11}$')
    bairro: Optional[str] = Field(None, max_length=100)
    zona: Optional[str] = Field(None, max_length=50)
    telefone: Optional[str] = Field(None, max_length=15, pattern=r'^[0-9]{10,11}$|^$')
    email: Optional[EmailStr] = None
    endereco_completo: Optional[str] = Field(None, max_length=200)
    programa_social: Optional[str] = Field(None, max_length=100)
    status_cadastro: Optional[str] = Field(None, max_length=50)
    ativo: Optional[bool] = None

from typing import Optional

class CidadaoInDB(CidadaoBase):
    id: int
    data_cadastro: Optional[date] = None
    data_atualizacao: Optional[date] = None
    ativo: bool = True
    votou: Optional[bool] = False
    elegivel: Optional[bool] = True

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat() if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }

class Cidadao(CidadaoInDB):
    pass
