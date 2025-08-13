# Inicializador do pacote de operações CRUD
from .cidadao import (
    get_cidadao,
    get_cidadao_by_cpf,
    get_cidadaos,
    create_cidadao,
    update_cidadao,
    delete_cidadao,
    count_cidadaos,
    search_cidadaos,
    atualizar_votou
)

__all__ = [
    # Funções de Cidadão
    'get_cidadao',
    'get_cidadao_by_cpf',
    'get_cidadaos',
    'create_cidadao',
    'update_cidadao',
    'delete_cidadao',
    'count_cidadaos',
    'search_cidadaos',
    'atualizar_votou'
]
