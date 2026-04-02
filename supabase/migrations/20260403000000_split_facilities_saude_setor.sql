-- session-036: Split setores "facilities" e "saude"
-- facilities → servicos_prediais (mais próximo do original - serviços)
-- saude → medicamentos (mais frequente nas licitações de saúde)

-- Split facilities: alertas existentes migram para servicos_prediais
UPDATE alerts
SET filters = jsonb_set(filters, '{setor}', '"servicos_prediais"')
WHERE filters->>'setor' = 'facilities';

-- Split saude: alertas existentes migram para medicamentos
UPDATE alerts
SET filters = jsonb_set(filters, '{setor}', '"medicamentos"')
WHERE filters->>'setor' = 'saude';
