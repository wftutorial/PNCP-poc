-- session-040 ISSUE-072: Split setor "software" em "software_desenvolvimento" + "software_licencas"
-- Alertas existentes migram para software_desenvolvimento (ICP primario — software houses)
-- Analogia: mesmo padrao do split transporte (20260402180000_split_transporte_setor.sql)

UPDATE alerts
SET filters = jsonb_set(filters, '{setor}', '"software_desenvolvimento"')
WHERE filters->>'setor' = 'software';

-- Historico de buscas e sessoes preservam o valor original "software" como snapshot historico.
-- Nenhuma outra tabela referencia setor_id diretamente.
