"""Prompt builders for LLM arbiter classification.

TD-009: Extracted from llm_arbiter.py as part of DEBT-07 module split.
Contains all prompt construction functions for sector/term/zero-match/batch modes.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# STORY-328 AC13: Dynamic negative examples per sector (org name traps)
_SECTOR_NEGATIVE_EXAMPLES: dict[str, list[str]] = {
    "servicos_prediais": [
        "aquisicao de material de limpeza",
        "compra de produto de limpeza",
        "detergente para uso domestico",
    ],
    "produtos_limpeza": [
        "servico de limpeza e conservacao predial",
        "terceirizacao de portaria e zeladoria",
        "empresa de limpeza contratada",
    ],
    "medicamentos": [
        "equipamento hospitalar tomografo",
        "seringa e agulha descartavel",
        "monitor multiparametro uti",
    ],
    "equipamentos_medicos": [
        "medicamento dipirona paracetamol",
        "vacina imunobiologico",
        "material descartavel seringa gaze",
    ],
    "insumos_hospitalares": [
        "medicamento farmacia basica",
        "equipamento de grande porte tomografo",
        "saneante hospitalar produto de limpeza",
    ],
    "informatica": [
        "Uniformes para Secretaria de Tecnologia",
        "Material de limpeza para Instituto de Tecnologia",
        "Reforma predial na Secretaria de Tecnologia da Informação",
    ],
    "vigilancia": [
        "Material de escritório para Secretaria de Segurança Pública",
        "Gêneros alimentícios para Departamento de Segurança",
        "Locação de veículos para Secretaria de Segurança",
    ],
    "vestuario": [
        "Equipamentos de informática para fábrica de confecções",
        "Manutenção predial em loja de roupas",
    ],
    "alimentos": [
        "Material de escritório para Secretaria de Alimentação",
        "Reforma na cozinha da Secretaria de Agricultura",
    ],
    "engenharia_rodoviaria": [
        "Material de escritório para Departamento de Estradas",
        "Uniformes para equipe de rodovias",
    ],
    "transporte_servicos": [
        "Material de escritório para Secretaria de Transportes",
        "Uniformes para Departamento de Trânsito",
        "Aquisição de veículos tipo ambulância para SAMU",
    ],
    "frota_veicular": [
        "Material de escritório para Secretaria de Transportes",
        "Uniformes para Departamento de Trânsito",
    ],
    "materiais_eletricos": [
        "Material de limpeza para Companhia de Energia",
        "Uniformes para equipe da Eletrobras",
    ],
    "materiais_hidraulicos": [
        "Material de escritório para SABESP",
        "Uniformes para equipe de saneamento",
    ],
    "mobiliario": [
        "Material de limpeza para fábrica de móveis",
        "Combustível para Secretaria de Administração",
    ],
    "papelaria": [
        "Combustível para gráfica municipal",
        "Uniformes para equipe de impressão",
    ],
    "software_desenvolvimento": [
        "Material de escritório para empresa de software",
        "Uniformes para equipe de TI",
    ],
    "software_licencas": [
        "Material de escritório para empresa de software",
        "Uniformes para equipe de TI",
    ],
    "manutencao_predial": [
        "Material de escritório para equipe de manutenção",
        "Gêneros alimentícios para prédio público",
    ],
}


def _get_sector_negative_examples(setor_id: str) -> list[str]:
    """Return dynamic negative examples for a sector (AC13)."""
    return _SECTOR_NEGATIVE_EXAMPLES.get(setor_id, [])


_STRUCTURED_JSON_INSTRUCTION = """
Responda em JSON com a estrutura exata:
{"classe": "SIM" ou "NAO", "confianca": 0-100, "evidencias": ["citação 1", "citação 2"], "motivo_exclusao": "razão se NAO", "precisa_mais_dados": false}

REGRAS:
- evidencias: use COPY-PASTE exato de trechos do campo Objeto acima — cada evidência DEVE ser uma substring que aparece literalmente no texto do Objeto, sem alterar, adicionar ou remover nenhuma palavra. Se não encontrar trecho literal relevante, retorne evidencias como lista vazia [].
- confianca: 100 se palavras-chave primárias presentes, 50 se ambíguo, 0 se claramente fora do setor
- motivo_exclusao: preencha APENAS quando classe="NAO"
- precisa_mais_dados: true se a descrição é muito curta/vaga para decidir"""


def _build_conservative_prompt(
    setor_id: Optional[str],
    setor_name: str,
    objeto_truncated: str,
    valor: float,
    structured: bool = False,
) -> str:
    """Build sector-aware conservative prompt with dynamic examples (STORY-251)."""
    from sectors import get_sector

    if not setor_id:
        return _build_standard_sector_prompt(setor_name, objeto_truncated, valor, structured)

    try:
        config = get_sector(setor_id)
    except (KeyError, Exception):
        logger.warning(f"Sector '{setor_id}' not found for conservative prompt, using standard")
        return _build_standard_sector_prompt(setor_name, objeto_truncated, valor, structured)

    description = config.description or setor_name
    keywords = sorted(config.keywords, key=len, reverse=True)[:3]
    sim_lines = "\n".join(f'- "Aquisição de {kw} para órgão público"' for kw in keywords)
    exclusions = sorted(config.exclusions)[:3]
    nao_section = ""
    if exclusions:
        nao_lines = "\n".join(f'- "{exc}"' for exc in exclusions)
        nao_section = f"\nNAO:\n{nao_lines}"

    suffix = _STRUCTURED_JSON_INSTRUCTION if structured else "\nResponda APENAS: SIM ou NAO"

    _neg_examples = _get_sector_negative_examples(setor_id)
    neg_section = ""
    if _neg_examples:
        neg_lines = "\n".join(f'- "{ex}" → NAO' for ex in _neg_examples)
        neg_section = f"\nARMADILHAS (contêm nome de órgão, NÃO são do setor):\n{neg_lines}"

    return f"""Você é um classificador de licitações públicas. Analise se o contrato é PRIMARIAMENTE sobre o setor especificado (> 80% do valor e escopo).

SETOR: {setor_name}
DESCRIÇÃO DO SETOR: {description}

ATENÇÃO CRÍTICA: O campo 'Objeto' pode conter o nome do órgão comprador (ex: 'Secretaria de Saúde', 'Secretaria de Tecnologia', 'Prefeitura Municipal'). IGNORE completamente nomes de órgãos, secretarias, hospitais, universidades e institutos. Foque EXCLUSIVAMENTE no que está sendo CONTRATADO ou ADQUIRIDO.

CONTRATO:
Valor: R$ {valor:,.2f}
Objeto: {objeto_truncated}

EXEMPLOS DE CLASSIFICAÇÃO:

SIM:
{sim_lines}
{nao_section}
{neg_section}

Este contrato é PRIMARIAMENTE sobre {setor_name}?{suffix}"""


def _build_standard_sector_prompt(
    setor_name: str,
    objeto_truncated: str,
    valor: float,
    structured: bool = False,
) -> str:
    """Build standard sector prompt without examples (density 3-8% or fallback)."""
    suffix = _STRUCTURED_JSON_INSTRUCTION if structured else "\nResponda APENAS: SIM ou NAO"

    return f"""Setor: {setor_name}
Valor: R$ {valor:,.2f}
Objeto: {objeto_truncated}

Este contrato é PRIMARIAMENTE sobre {setor_name}?{suffix}"""


def _build_term_search_prompt(
    termos: list[str],
    objeto_truncated: str,
    valor: float,
    structured: bool = False,
) -> str:
    """STORY-267 AC1: Build term-aware prompt for custom search terms."""
    termos_display = ", ".join(termos)
    valor_display = f"R$ {valor:,.2f}" if valor > 0 else "Não informado"
    suffix = _STRUCTURED_JSON_INSTRUCTION if structured else "\nResponda APENAS: SIM ou NAO"

    return f"""Você classifica licitações públicas. O usuário buscou os seguintes termos:
Termos buscados: {termos_display}

CONTRATO:
Valor: {valor_display}
Objeto: {objeto_truncated}

Este contrato é RELEVANTE para alguém que busca "{termos_display}"?
Considere: o objeto deve ser PRIMARIAMENTE sobre os termos buscados, não apenas mencioná-los de forma tangencial.{suffix}"""


def _build_zero_match_prompt(
    setor_id: Optional[str],
    setor_name: str,
    objeto_truncated: str,
    valor: float,
    structured: bool = False,
) -> str:
    """Build sector-aware prompt for bids with ZERO keyword matches (GTM-FIX-028 AC4)."""
    from sectors import get_sector

    valor_display = f"R$ {valor:,.2f}" if valor > 0 else "Não informado"
    suffix = _STRUCTURED_JSON_INSTRUCTION if structured else "\nResponda APENAS: SIM ou NAO"

    if not setor_id:
        return f"""SETOR: {setor_name}

CONTRATO:
Valor: {valor_display}
Objeto: {objeto_truncated}

Este contrato é sobre {setor_name}?{suffix}"""

    try:
        config = get_sector(setor_id)
    except (KeyError, Exception):
        logger.warning(f"Sector '{setor_id}' not found for zero_match prompt, using fallback")
        return f"""SETOR: {setor_name}

CONTRATO:
Valor: {valor_display}
Objeto: {objeto_truncated}

Este contrato é sobre {setor_name}?{suffix}"""

    description = config.description or setor_name
    keywords = sorted(config.keywords, key=len, reverse=True)[:5]
    sim_lines = "\n".join(f'- "{kw}"' for kw in keywords)
    exclusions = sorted(config.exclusions)[:3]
    nao_section = ""
    if exclusions:
        nao_lines = "\n".join(f'- "{exc}"' for exc in exclusions)
        nao_section = f"\nExemplos de NÃO (não é sobre o setor):\n{nao_lines}"

    _neg_examples = _get_sector_negative_examples(setor_id)
    neg_section = ""
    if _neg_examples:
        neg_lines = "\n".join(f'- "{ex}" → NAO' for ex in _neg_examples)
        neg_section = f"\nExemplos de ARMADILHA (contêm nome de órgão, NÃO são do setor):\n{neg_lines}"

    return f"""Você classifica licitações públicas. Este contrato NÃO contém palavras-chave do setor — analise o OBJETO para determinar se é relevante.

REGRA CRÍTICA: É MUITO PIOR marcar um contrato irrelevante como SIM do que perder um contrato relevante. Na dúvida, responda NAO.

SETOR: {setor_name}
DESCRIÇÃO: {description}

ATENÇÃO CRÍTICA: O campo 'Objeto' pode conter o nome do órgão comprador (ex: 'Secretaria de Saúde', 'Secretaria de Tecnologia', 'Prefeitura Municipal'). IGNORE completamente nomes de órgãos, secretarias, hospitais, universidades e institutos. Foque EXCLUSIVAMENTE no que está sendo CONTRATADO ou ADQUIRIDO.
O contrato DEVE ser DIRETAMENTE sobre aquisição, fornecimento ou confecção de itens do setor como OBJETO PRINCIPAL. Contratos onde o setor aparece apenas como item secundário, acessório ou condição NÃO são relevantes.

Exemplos de SIM (é sobre o setor):
{sim_lines}
{nao_section}
{neg_section}

CONTRATO:
Valor: {valor_display}
Objeto: {objeto_truncated}

Este contrato é DIRETAMENTE e PRINCIPALMENTE sobre {setor_name}?{suffix}"""


def _build_zero_match_batch_prompt(
    setor_id: Optional[str],
    setor_name: str,
    items: list[dict],
) -> str:
    """Build a batch prompt for classifying multiple zero-match items at once (AC1)."""
    from sectors import get_sector

    description = setor_name
    keywords_section = ""
    exclusions_section = ""
    neg_section = ""

    if setor_id:
        try:
            config = get_sector(setor_id)
            description = config.description or setor_name
            keywords = sorted(config.keywords, key=len, reverse=True)[:5]
            keywords_section = "\nPalavras-chave do setor: " + ", ".join(keywords)
            exclusions = sorted(config.exclusions)[:3]
            if exclusions:
                exclusions_section = "\nExemplos de NÃO: " + ", ".join(exclusions)
            _neg_examples = _get_sector_negative_examples(setor_id)
            if _neg_examples:
                neg_lines = "; ".join(_neg_examples[:3])
                neg_section = f"\nARMADILHAS (nome de órgão ≠ setor): {neg_lines}"
        except (KeyError, Exception):
            logger.warning(f"Sector '{setor_id}' not found for batch prompt, using fallback")

    item_lines = []
    for i, item in enumerate(items, 1):
        obj = item["objeto"][:200]
        val = item["valor"]
        val_display = f"R$ {val:,.2f}" if val > 0 else "N/I"
        item_lines.append(f"{i}. [{val_display}] {obj}")

    items_text = "\n".join(item_lines)

    return f"""Você classifica licitações públicas em lote. Analise cada contrato e determine se é PRIMARIAMENTE sobre o setor especificado.

SETOR: {setor_name}
DESCRIÇÃO: {description}
{keywords_section}
{exclusions_section}
{neg_section}

ATENÇÃO: IGNORE nomes de órgãos/secretarias. Foque no que está sendo CONTRATADO.

CONTRATOS:
{items_text}

Responda APENAS com uma lista numerada de YES ou NO, uma por linha. Exemplo:
1. YES
2. NO
3. YES"""


def _build_zero_match_batch_prompt_terms(
    termos: list[str],
    items: list[dict],
) -> str:
    """Build a batch prompt for term-based zero-match classification (AC1)."""
    termos_display = ", ".join(termos)

    item_lines = []
    for i, item in enumerate(items, 1):
        obj = item["objeto"][:200]
        val = item["valor"]
        val_display = f"R$ {val:,.2f}" if val > 0 else "N/I"
        item_lines.append(f"{i}. [{val_display}] {obj}")

    items_text = "\n".join(item_lines)

    return f"""Classifique cada licitação: o objeto trata DIRETAMENTE dos termos buscados?

Termos buscados: {termos_display}

REGRAS ESTRITAS:
- YES SOMENTE se o objeto é sobre o MESMO tipo de produto/serviço/obra dos termos.
  Exemplo correto: termos="uniformes escolares" e objeto="aquisição de uniformes para alunos" → YES
- NO se o objeto é sobre OUTRO assunto, mesmo que vagamente relacionado.
  Exemplo: termos="uniformes escolares" e objeto="construção de escola" → NO
  Exemplo: termos="pavimentação" e objeto="quadros digitais interativos" → NO
  Exemplo: termos="uniformes escolares" e objeto="material de informática" → NO
  Exemplo: termos="uniformes escolares" e objeto="serviços de engenharia" → NO
- NO se os termos aparecem apenas no nome do órgão, secretaria ou endereço.
- NO se o objeto é genérico (material de escritório, limpeza, informática, alimentos) e NÃO trata especificamente dos termos.
- NA DÚVIDA, responda NO.

CONTRATOS:
{items_text}

Responda APENAS com lista numerada YES/NO:
1. YES
2. NO
3. YES"""
