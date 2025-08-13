-- Migração para remover a coluna 'votou' da tabela 'cidadaos'
-- Data: 2025-08-11

-- Remove a coluna 'votou' se ela existir
ALTER TABLE cidadaos 
DROP COLUMN IF EXISTS votou;
