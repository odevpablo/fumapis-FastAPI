import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:{password}@localhost:5432/fumapis")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clean_null_values(instance):
    """
    Limpa valores nulos e vazios em um objeto SQLAlchemy.
    Converte strings vazias, 'NULL' (case insensitive) e strings contendo apenas espaços para None.
    """
    if instance is None:
        return
        
    # Lista de campos que devem ser limpos
    fields_to_clean = [
        'cpf', 'cpf_conjuge', 'telefone', 'email', 
        'nome_conjuge', 'programa_social', 'endereco_completo',
        'bairro', 'status_cadastro', 'nome_completo',
        'endereco', 'cidade', 'estado', 'cep', 'rg', 'orgao_emissor',
        'titulo_eleitor', 'zona_eleitoral', 'secao_eleitoral',
        'nome_mae', 'nome_pai', 'naturalidade', 'nacionalidade',
        'estado_civil', 'grau_instrucao', 'profissao', 'renda_mensal'
    ]
    
    for field in fields_to_clean:
        if hasattr(instance, field):
            value = getattr(instance, field)
            
            # Verifica se o valor é uma string vazia, 'NULL' ou contém apenas espaços
            if isinstance(value, str):
                value = value.strip()
                if value.upper() == 'NULL' or value == '':
                    setattr(instance, field, None)
                else:
                    # Remove espaços extras
                    setattr(instance, field, value.strip() if value else None)
            # Se o valor for None, garante que está definido como None
            elif value is None:
                setattr(instance, field, None)

# Adiciona um listener para limpar valores 'NULL' após carregar um objeto
@event.listens_for(Session, 'loaded_as_persistent')
def load_listener(session, instance):
    clean_null_values(instance)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
