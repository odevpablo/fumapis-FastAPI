# Inicializador do pacote models
from .user import UserDB, UserCreate, UserInDB, UserOut
from .cidadao import Cidadao
from .base import Base

__all__ = [
    'UserDB', 'UserCreate', 'UserInDB', 'UserOut',  # Modelos de usuário
    'Cidadao',  # Modelo de cidadão
    'Base'      # Base para os modelos
]
