-- Migração para adicionar a coluna 'votou' na tabela 'cidadaos'
-- Data: 2025-08-11

-- Adiciona a coluna 'votou' com valor padrão FALSE
ALTER TABLE cidadaos 
ADD COLUMN IF NOT EXISTS votou BOOLEAN NOT NULL DEFAULT FALSE;

-- Atualiza o comentário da coluna (opcional, dependendo do seu banco de dados)
COMMENT ON COLUMN cidadaos.votou IS 'Indica se o cidadão já votou';

-- Para PostgreSQL, você pode usar o seguinte para garantir que a restrição NOT NULL seja aplicada corretamente:
-- ALTER TABLE cidadaos ALTER COLUMN votou SET NOT NULL;
