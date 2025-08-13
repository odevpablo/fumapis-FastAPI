from app.database import engine
from app.models.base import Base
from app.models.cidadao import Cidadao

def create_tables():
    print("Criando tabela de cidadãos...")
    # Cria apenas a tabela de cidadãos
    Cidadao.__table__.create(bind=engine, checkfirst=True)
    print("Tabela 'cidadaos' criada com sucesso!")

if __name__ == "__main__":
    create_tables()
