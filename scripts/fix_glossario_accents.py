import re

with open('D:/pncp-poc/frontend/app/glossario/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    # -cao / -coes
    ('Adjudicacao', 'Adjudicação'), ('adjudicacao', 'adjudicação'),
    ('Habilitacao', 'Habilitação'), ('habilitacao', 'habilitação'),
    ('Homologacao', 'Homologação'), ('homologacao', 'homologação'),
    ('Impugnacao', 'Impugnação'), ('impugnacao', 'impugnação'),
    ('Fiscalizacao', 'Fiscalização'), ('fiscalizacao', 'fiscalização'),
    ('Execucao', 'Execução'), ('execucao', 'execução'),
    ('Medicao', 'Medição'), ('medicao', 'medição'),
    ('Contratacoes', 'Contratações'), ('contratacoes', 'contratações'),
    ('Contratacao', 'Contratação'), ('contratacao', 'contratação'),
    ('Publicacoes', 'Publicações'), ('publicacoes', 'publicações'),
    ('Publicacao', 'Publicação'), ('publicacao', 'publicação'),
    ('Licitacoes', 'Licitações'), ('licitacoes', 'licitações'),
    ('Licitacao', 'Licitação'), ('licitacao', 'licitação'),
    ('Selecao', 'Seleção'), ('selecao', 'seleção'),
    ('Sancoes', 'Sanções'), ('sancoes', 'sanções'),
    ('Sancao', 'Sanção'), ('sancao', 'sanção'),
    ('Revogacao', 'Revogação'), ('revogacao', 'revogação'),
    ('Anulacao', 'Anulação'), ('anulacao', 'anulação'),
    ('Dotacao', 'Dotação'), ('dotacao', 'dotação'),
    ('Concorrencia', 'Concorrência'), ('concorrencia', 'concorrência'),
    ('Aquisicao', 'Aquisição'), ('aquisicao', 'aquisição'),
    ('Alienacao', 'Alienação'), ('alienacao', 'alienação'),
    ('Avaliacao', 'Avaliação'), ('avaliacao', 'avaliação'),
    ('Gestao', 'Gestão'), ('gestao', 'gestão'),
    ('Situacao', 'Situação'), ('situacao', 'situação'),
    ('Autorizacao', 'Autorização'), ('autorizacao', 'autorização'),
    ('Aprovacao', 'Aprovação'), ('aprovacao', 'aprovação'),
    ('Manutencao', 'Manutenção'), ('manutencao', 'manutenção'),
    ('Regularizacao', 'Regularização'), ('regularizacao', 'regularização'),
    ('Negociacao', 'Negociação'), ('negociacao', 'negociação'),
    ('Participacao', 'Participação'), ('participacao', 'participação'),
    ('Classificacao', 'Classificação'), ('classificacao', 'classificação'),
    ('Qualificacao', 'Qualificação'), ('qualificacao', 'qualificação'),
    ('Verificacao', 'Verificação'), ('verificacao', 'verificação'),
    ('Composicao', 'Composição'), ('composicao', 'composição'),
    ('Reducao', 'Redução'), ('reducao', 'redução'),
    ('Punicao', 'Punição'), ('punicao', 'punição'),
    ('Adequacao', 'Adequação'), ('adequacao', 'adequação'),
    ('Elaboracao', 'Elaboração'), ('elaboracao', 'elaboração'),
    ('Atualizacao', 'Atualização'), ('atualizacao', 'atualização'),
    ('Restricoes', 'Restrições'), ('restricoes', 'restrições'),
    ('Restricao', 'Restrição'), ('restricao', 'restrição'),
    ('Comparacao', 'Comparação'), ('comparacao', 'comparação'),
    ('Substituicao', 'Substituição'), ('substituicao', 'substituição'),
    ('Conclusao', 'Conclusão'), ('conclusao', 'conclusão'),
    ('Rescisao', 'Rescisão'), ('rescisao', 'rescisão'),
    ('Inscricao', 'Inscrição'), ('inscricao', 'inscrição'),
    ('Inclusao', 'Inclusão'), ('inclusao', 'inclusão'),
    ('Exclusao', 'Exclusão'), ('exclusao', 'exclusão'),
    ('Protecao', 'Proteção'), ('protecao', 'proteção'),
    ('Constituicao', 'Constituição'), ('constituicao', 'constituição'),
    ('Vinculacao', 'Vinculação'), ('vinculacao', 'vinculação'),
    ('Convocacao', 'Convocação'), ('convocacao', 'convocação'),
    ('Atribuicao', 'Atribuição'), ('atribuicao', 'atribuição'),
    ('Versao', 'Versão'), ('versao', 'versão'),
    ('Previsao', 'Previsão'), ('previsao', 'previsão'),
    ('Informacoes', 'Informações'), ('informacoes', 'informações'),
    ('Informacao', 'Informação'), ('informacao', 'informação'),
    ('Condicoes', 'Condições'), ('condicoes', 'condições'),
    ('Condicao', 'Condição'), ('condicao', 'condição'),
    ('Obrigacoes', 'Obrigações'), ('obrigacoes', 'obrigações'),
    ('Obrigacao', 'Obrigação'), ('obrigacao', 'obrigação'),
    ('Emissao', 'Emissão'), ('emissao', 'emissão'),
    ('Declaracao', 'Declaração'), ('declaracao', 'declaração'),
    ('Operacao', 'Operação'), ('operacao', 'operação'),
    ('Suspensao', 'Suspensão'), ('suspensao', 'suspensão'),
    ('Sessao', 'Sessão'), ('sessao', 'sessão'),
    ('Inversao', 'Inversão'), ('inversao', 'inversão'),
    ('Interrupcao', 'Interrupção'), ('interrupcao', 'interrupção'),
    ('Definicoes', 'Definições'), ('definicoes', 'definições'),
    ('Aplicacao', 'Aplicação'), ('aplicacao', 'aplicação'),
    ('Obtencao', 'Obtenção'), ('obtencao', 'obtenção'),
    ('Comprovacao', 'Comprovação'), ('comprovacao', 'comprovação'),
    ('Desclassificacao', 'Desclassificação'), ('desclassificacao', 'desclassificação'),
    ('Inabilitacao', 'Inabilitação'), ('inabilitacao', 'inabilitação'),
    ('Lancamentos', 'Lançamentos'), ('lancamentos', 'lançamentos'),
    ('Lancamento', 'Lançamento'), ('lancamento', 'lançamento'),
    ('Excecao', 'Exceção'), ('excecao', 'exceção'),
    ('Opcao', 'Opção'), ('opcao', 'opção'),
    ('Relacao', 'Relação'), ('relacao', 'relação'),
    ('Mediacao', 'Mediação'), ('mediacao', 'mediação'),
    ('Funcoes', 'Funções'), ('funcoes', 'funções'),
    ('Funcao', 'Função'), ('funcao', 'função'),
    # Proper nouns / other
    ('Glossario', 'Glossário'), ('glossario', 'glossário'),
    ('Dialogo', 'Diálogo'), ('dialogo', 'diálogo'),
    ('Consorcio', 'Consórcio'), ('consorcio', 'consórcio'),
    ('Leilao', 'Leilão'), ('leilao', 'leilão'),
    ('Pregao', 'Pregão'), ('pregao', 'pregão'),
    # Eletrônico
    ('Eletronicos', 'Eletrônicos'), ('eletronicos', 'eletrônicos'),
    ('Eletronico', 'Eletrônico'), ('eletronico', 'eletrônico'),
    ('Eletronica', 'Eletrônica'), ('eletronica', 'eletrônica'),
    # Órgão
    ('Orgaos', 'Órgãos'), ('orgaos', 'órgãos'),
    ('Orgao', 'Órgão'), ('orgao', 'órgão'),
    # Orçamento
    ('Orcamentaria', 'Orçamentária'), ('orcamentaria', 'orçamentária'),
    ('Orcamento', 'Orçamento'), ('orcamento', 'orçamento'),
    # Público
    ('Publicos', 'Públicos'), ('publicos', 'públicos'),
    ('Publicas', 'Públicas'), ('publicas', 'públicas'),
    ('Publico', 'Público'), ('publico', 'público'),
    ('Publica', 'Pública'), ('publica', 'pública'),
    # Técnico
    ('Tecnicos', 'Técnicos'), ('tecnicos', 'técnicos'),
    ('Tecnicas', 'Técnicas'), ('tecnicas', 'técnicas'),
    ('Tecnico', 'Técnico'), ('tecnico', 'técnico'),
    ('Tecnica', 'Técnica'), ('tecnica', 'técnica'),
    # Específico
    ('Especificos', 'Específicos'), ('especificos', 'específicos'),
    ('Especificas', 'Específicas'), ('especificas', 'específicas'),
    ('Especifico', 'Específico'), ('especifico', 'específico'),
    ('Especifica', 'Específica'), ('especifica', 'específica'),
    # Único
    ('Unicos', 'Únicos'), ('unicos', 'únicos'),
    ('Unicas', 'Únicas'), ('unicas', 'únicas'),
    ('Unico', 'Único'), ('unico', 'único'),
    ('Unica', 'Única'), ('unica', 'única'),
    # Jurídico
    ('Juridicos', 'Jurídicos'), ('juridicos', 'jurídicos'),
    ('Juridicas', 'Jurídicas'), ('juridicas', 'jurídicas'),
    ('Juridico', 'Jurídico'), ('juridico', 'jurídico'),
    ('Juridica', 'Jurídica'), ('juridica', 'jurídica'),
    # Obrigatório
    ('Obrigatorios', 'Obrigatórios'), ('obrigatorios', 'obrigatórios'),
    ('Obrigatorias', 'Obrigatórias'), ('obrigatorias', 'obrigatórias'),
    ('Obrigatorio', 'Obrigatório'), ('obrigatorio', 'obrigatório'),
    ('Obrigatoria', 'Obrigatória'), ('obrigatoria', 'obrigatória'),
    # Licitatório
    ('licitatorios', 'licitatórios'), ('licitatorias', 'licitatórias'),
    ('licitatorio', 'licitatório'), ('licitatoria', 'licitatória'),
    # Prática
    ('Praticas', 'Práticas'), ('praticas', 'práticas'),
    ('Pratico', 'Prático'), ('pratico', 'prático'),
    ('Pratica', 'Prática'), ('pratica', 'prática'),
    # Própria
    ('Proprias', 'Próprias'), ('proprias', 'próprias'),
    ('Proprios', 'Próprios'), ('proprios', 'próprios'),
    ('Propria', 'Própria'), ('propria', 'própria'),
    ('Proprio', 'Próprio'), ('proprio', 'próprio'),
    # Econômico
    ('Economicos', 'Econômicos'), ('economicos', 'econômicos'),
    ('Economicas', 'Econômicas'), ('economicas', 'econômicas'),
    ('Economico', 'Econômico'), ('economico', 'econômico'),
    ('Economica', 'Econômica'), ('economica', 'econômica'),
    # Critério
    ('Criterios', 'Critérios'), ('criterios', 'critérios'),
    ('Criterio', 'Critério'), ('criterio', 'critério'),
    # Número
    ('Numeros', 'Números'), ('numeros', 'números'),
    ('Numero', 'Número'), ('numero', 'número'),
    # Período
    ('Periodos', 'Períodos'), ('periodos', 'períodos'),
    ('Periodo', 'Período'), ('periodo', 'período'),
    ('Periodicos', 'Periódicos'), ('periodicos', 'periódicos'),
    ('Periodico', 'Periódico'), ('periodico', 'periódico'),
    ('Periodica', 'Periódica'), ('periodica', 'periódica'),
    # Máximo/mínimo
    ('Maximo', 'Máximo'), ('maximo', 'máximo'),
    ('Maxima', 'Máxima'), ('maxima', 'máxima'),
    ('Minimos', 'Mínimos'), ('minimos', 'mínimos'),
    ('Minimo', 'Mínimo'), ('minimo', 'mínimo'),
    ('Minima', 'Mínima'), ('minima', 'mínima'),
    # Último
    ('Ultimas', 'Últimas'), ('ultimas', 'últimas'),
    ('Ultimos', 'Últimos'), ('ultimos', 'últimos'),
    ('Ultima', 'Última'), ('ultima', 'última'),
    ('Ultimo', 'Último'), ('ultimo', 'último'),
    # Básico
    ('Basicos', 'Básicos'), ('basicos', 'básicos'),
    ('Basicas', 'Básicas'), ('basicas', 'básicas'),
    ('Basico', 'Básico'), ('basico', 'básico'),
    ('Basica', 'Básica'), ('basica', 'básica'),
    # Referência
    ('Referencias', 'Referências'), ('referencias', 'referências'),
    ('Referencia', 'Referência'), ('referencia', 'referência'),
    # Cláusula
    ('Clausulas', 'Cláusulas'), ('clausulas', 'cláusulas'),
    ('Clausula', 'Cláusula'), ('clausula', 'cláusula'),
    # Prévia
    ('Previas', 'Prévias'), ('previas', 'prévias'),
    ('Previa', 'Prévia'), ('previa', 'prévia'),
    ('Previo', 'Prévio'), ('previo', 'prévio'),
    # Reequilíbrio
    ('Reequilibrio', 'Reequilíbrio'), ('reequilibrio', 'reequilíbrio'),
    # Após
    ('Apos ', 'Após '), ('apos ', 'após '),
    # prorrogavel
    ('prorrogavel', 'prorrogável'), ('Prorrogavel', 'Prorrogável'),
    # vinculativo
    ('vinculativo', 'vinculativo'),  # already correct
    # criterio de julgamento
    # arrematados - correct
    # arrematado - correct
    # simplifica - correct
    # centralizacao
    ('Centralizacao', 'Centralização'), ('centralizacao', 'centralização'),
    # Indexação
    ('Indexacao', 'Indexação'), ('indexacao', 'indexação'),
]

for old, new in replacements:
    content = content.replace(old, new)

# Word-boundary replacements
content = re.sub(r'\bnao\b', 'não', content)
content = re.sub(r'\bNao\b', 'Não', content)
content = re.sub(r'\bate\b', 'até', content)
content = re.sub(r'\bAte\b', 'Até', content)

with open('D:/pncp-poc/frontend/app/glossario/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")

# Spot check
checks = ['Glossario', 'licitacao', 'Habilitacao', 'pregao', 'eletronico',
          'orgao', 'obrigatorio', 'pratica ', 'tecnico', 'juridico',
          'publico', 'especifico', ' nao ', ' ate ']
for p in checks:
    count = content.count(p)
    status = "STILL HAS" if count > 0 else "OK"
    print(f"  {status}: '{p}' ({count}x)")
