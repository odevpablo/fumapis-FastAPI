from app.database import engine
from app.models.base import Base
from app.models.eleitor import Eleitor

def create_tables():
    print("Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    create_tables()
