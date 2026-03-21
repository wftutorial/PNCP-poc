"""Tests for scripts/lib/doc_templates.py — structured extraction templates."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure scripts/ is importable
SCRIPTS_DIR = Path(__file__).parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.doc_templates import (
    DocType,
    ExtractedField,
    StructuredExtraction,
    _search_pattern,
    detect_doc_type,
    extract_all_types,
    extract_structured,
    merge_extractions,
)


# ============================================================
# DOCUMENT TYPE DETECTION
# ============================================================


class TestDetectDocType:
    def test_edital_from_title(self):
        assert detect_doc_type("Edital de Pregao Eletronico 001/2026") == DocType.EDITAL

    def test_edital_from_aviso(self):
        assert detect_doc_type("Aviso de Licitacao") == DocType.EDITAL

    def test_concorrencia(self):
        assert detect_doc_type("Concorrencia Publica 005/2026") == DocType.EDITAL

    def test_termo_referencia(self):
        assert detect_doc_type("Termo de Referencia - Pavimentacao") == DocType.TERMO_REFERENCIA

    def test_tr_abbreviation(self):
        assert detect_doc_type("TR completo") == DocType.TERMO_REFERENCIA

    def test_projeto_basico(self):
        assert detect_doc_type("Projeto Basico de Engenharia") == DocType.TERMO_REFERENCIA

    def test_planilha(self):
        assert detect_doc_type("Planilha Orcamentaria") == DocType.PLANILHA

    def test_bdi(self):
        assert detect_doc_type("Composicao de BDI") == DocType.PLANILHA

    def test_quantitativo(self):
        assert detect_doc_type("Planilha de Quantitativo") == DocType.PLANILHA

    def test_unknown(self):
        assert detect_doc_type("Ata de Reuniao") == DocType.UNKNOWN

    def test_filename_also_checked(self):
        assert detect_doc_type("Documento", "edital_completo.pdf") == DocType.EDITAL


# ============================================================
# PATRIMONIO LIQUIDO EXTRACTION
# ============================================================


class TestPatrimonioLiquido:
    def test_standard_format(self):
        text = "O patrimonio liquido minimo de R$ 500.000,00 conforme item 8.3."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("patrimonio_liquido")
        assert field is not None
        assert field.found is True
        assert "500.000,00" in field.value

    def test_pl_abbreviation(self):
        text = "PL minimo de R$ 200.000,00 para participacao."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("patrimonio_liquido")
        assert field.found is True

    def test_percentage_format(self):
        text = "10% do valor da contratacao como patrimonio liquido minimo."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("patrimonio_liquido")
        assert field.found is True

    def test_qualificacao_economica_pattern(self):
        text = "qualificacao economica: patrimonio liquido comprovado."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("patrimonio_liquido")
        assert field.found is True

    def test_not_found(self):
        text = "Este edital trata de servicos de limpeza."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("patrimonio_liquido")
        assert field.found is False


# ============================================================
# ACERVO TECNICO / CAT
# ============================================================


class TestAcervoTecnico:
    def test_cat_crea(self):
        text = "Acervo tecnico: CAT emitida pelo CREA comprovando execucao de obra similar."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("acervo_tecnico")
        assert field.found is True

    def test_atestado_capacidade(self):
        text = "Atestado de capacidade tecnica comprovando execucao de pavimentacao."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("acervo_tecnico")
        assert field.found is True

    def test_capacidade_profissional(self):
        text = "Capacidade tecnico profissional comprovada mediante atestado."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("acervo_tecnico")
        assert field.found is True


# ============================================================
# GARANTIA
# ============================================================


class TestGarantia:
    def test_garantia_proposta_pct(self):
        text = "Garantia de proposta de 1% do valor estimado."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("garantia_proposta")
        assert field.found is True

    def test_seguro_garantia(self):
        text = "Seguro-garantia no valor de 5% do contrato."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("garantia_proposta")
        assert field.found is True

    def test_garantia_contratual(self):
        text = "Garantia contratual de 5% sobre o valor global."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("garantia_proposta")
        assert field.found is True

    def test_caucao(self):
        text = "Caucao em dinheiro de R$ 50.000,00 como garantia."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("garantia_proposta")
        assert field.found is True


# ============================================================
# PRAZO DE EXECUCAO
# ============================================================


class TestPrazoExecucao:
    def test_meses(self):
        text = "O prazo de execucao sera de 12 meses contados da ordem de servico."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("prazo_execucao")
        assert field.found is True
        assert "12" in field.value

    def test_dias_corridos(self):
        text = "Prazo de execucao de 180 dias corridos a partir da assinatura."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("prazo_execucao")
        assert field.found is True
        assert "180" in field.value

    def test_not_found(self):
        text = "Este documento nao especifica prazos."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("prazo_execucao")
        assert field.found is False


# ============================================================
# DATA DA SESSAO
# ============================================================


class TestDataSessao:
    def test_sessao_publica(self):
        text = "A sessao publica sera realizada em 15/04/2026 as 10h00."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("data_sessao")
        assert field.found is True
        assert "15/04/2026" in field.value

    def test_data_abertura(self):
        text = "Data da abertura das propostas: 20/05/2026."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("data_sessao")
        assert field.found is True


# ============================================================
# VISITA TECNICA
# ============================================================


class TestVisitaTecnica:
    def test_obrigatoria(self):
        text = "A visita tecnica sera obrigatoria para todos os licitantes."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("visita_tecnica")
        assert field.found is True
        assert "obrigat" in field.raw_match.lower()

    def test_facultativa(self):
        text = "Visita tecnica sera facultativa conforme item 5.2."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("visita_tecnica")
        assert field.found is True

    def test_vistoria(self):
        text = "Vistoria obrigatoria no local da obra."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("visita_tecnica")
        assert field.found is True


# ============================================================
# CONSORCIO
# ============================================================


class TestConsorcio:
    def test_vedado(self):
        text = "Consorcio vedado nesta licitacao."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("consorcio")
        assert field.found is True

    def test_permitido(self):
        text = "Consorcio permitido conforme regras do edital."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("consorcio")
        assert field.found is True

    def test_not_mentioned(self):
        text = "Servicos de limpeza e conservacao."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("consorcio")
        assert field.found is False


# ============================================================
# EXCLUSIVIDADE ME/EPP
# ============================================================


class TestExclusividadeMeEpp:
    def test_exclusivo_me(self):
        text = "Licitacao exclusiva para ME e EPP conforme LC 123."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("exclusividade_me_epp")
        assert field.found is True

    def test_cota_reservada(self):
        text = "Cota reservada de 25% para microempresas."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("exclusividade_me_epp")
        assert field.found is True

    def test_lc_123(self):
        text = "Nos termos da LC 123 com exclusividade para ME."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields.get("exclusividade_me_epp")
        assert field.found is True


# ============================================================
# TEMPLATE SELECTION BY DOC TYPE
# ============================================================


class TestTemplateSelection:
    def test_edital_has_patrimonio(self):
        result = extract_structured("texto qualquer", DocType.EDITAL)
        assert "patrimonio_liquido" in result.fields

    def test_tr_has_escopo(self):
        result = extract_structured("texto qualquer", DocType.TERMO_REFERENCIA)
        assert "escopo_tecnico" in result.fields

    def test_planilha_has_valor_total(self):
        result = extract_structured("texto qualquer", DocType.PLANILHA)
        assert "valor_total" in result.fields

    def test_unknown_falls_back_to_edital(self):
        result = extract_structured("texto qualquer", DocType.UNKNOWN)
        assert "patrimonio_liquido" in result.fields

    def test_string_doc_type(self):
        result = extract_structured("texto", "edital")
        assert result.doc_type == DocType.EDITAL

    def test_invalid_string_doc_type(self):
        result = extract_structured("texto", "invalid_type")
        assert result.doc_type == DocType.UNKNOWN


# ============================================================
# NO MATCHING PATTERNS
# ============================================================


class TestNoMatches:
    def test_empty_text(self):
        result = extract_structured("", DocType.EDITAL)
        assert result.found_fields == 0
        assert result.completeness_pct == 0.0

    def test_irrelevant_text(self):
        text = "Lorem ipsum dolor sit amet consectetur adipiscing elit."
        result = extract_structured(text, DocType.EDITAL)
        assert result.found_fields == 0


# ============================================================
# NUMBER FORMATS
# ============================================================


class TestNumberFormats:
    def test_brazilian_format(self):
        text = "Patrimonio liquido minimo de R$ 1.000.000,00."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields["patrimonio_liquido"]
        assert field.found is True
        assert "1.000.000,00" in field.value

    def test_no_spaces(self):
        text = "Patrimonio liquido minimo de R$500000."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields["patrimonio_liquido"]
        assert field.found is True


# ============================================================
# COMPLETENESS
# ============================================================


class TestCompleteness:
    def test_completeness_percentage(self):
        result = StructuredExtraction(total_fields=10, found_fields=5)
        assert result.completeness_pct == 50.0

    def test_completeness_zero_fields(self):
        result = StructuredExtraction(total_fields=0, found_fields=0)
        assert result.completeness_pct == 0.0

    def test_get_with_default(self):
        result = StructuredExtraction()
        result.fields["test"] = ExtractedField(found=False)
        assert result.get("test") == "Nao consta no edital disponivel"

    def test_get_found_value(self):
        result = StructuredExtraction()
        result.fields["test"] = ExtractedField(found=True, value="R$ 500.000")
        assert result.get("test") == "R$ 500.000"


# ============================================================
# MERGE EXTRACTIONS
# ============================================================


class TestMergeExtractions:
    def test_keeps_highest_confidence(self):
        ext1 = StructuredExtraction()
        ext1.fields["patrimonio_liquido"] = ExtractedField(found=True, value="R$ 500k", confidence=0.7)

        ext2 = StructuredExtraction()
        ext2.fields["patrimonio_liquido"] = ExtractedField(found=True, value="R$ 500.000,00", confidence=0.9)

        merged = merge_extractions([ext1, ext2])
        assert merged["patrimonio_liquido"].value == "R$ 500.000,00"

    def test_skips_not_found(self):
        ext1 = StructuredExtraction()
        ext1.fields["patrimonio_liquido"] = ExtractedField(found=False, value="")

        ext2 = StructuredExtraction()
        ext2.fields["patrimonio_liquido"] = ExtractedField(found=True, value="R$ 100k", confidence=0.6)

        merged = merge_extractions([ext1, ext2])
        assert merged["patrimonio_liquido"].value == "R$ 100k"

    def test_empty_extractions(self):
        merged = merge_extractions([])
        assert merged == {}

    def test_different_fields_combined(self):
        ext1 = StructuredExtraction()
        ext1.fields["patrimonio_liquido"] = ExtractedField(found=True, value="500k", confidence=0.8)

        ext2 = StructuredExtraction()
        ext2.fields["prazo_execucao"] = ExtractedField(found=True, value="180 dias", confidence=0.9)

        merged = merge_extractions([ext1, ext2])
        assert "patrimonio_liquido" in merged
        assert "prazo_execucao" in merged


# ============================================================
# EXTRACT ALL TYPES
# ============================================================


class TestExtractAllTypes:
    def test_returns_all_types(self):
        text = "patrimonio liquido minimo de R$ 100.000,00. BDI de 25,50%."
        results = extract_all_types(text)
        assert "edital" in results
        assert "termo_referencia" in results
        assert "planilha" in results
        assert "_best_type" in results

    def test_best_type_selected(self):
        text = "patrimonio liquido de R$ 100.000,00. Garantia de proposta 1%. Visita tecnica obrigatoria."
        results = extract_all_types(text)
        # Edital patterns should match more
        assert results["_best_type"] in ("edital", "termo_referencia", "planilha")


# ============================================================
# CONFIDENCE ORDERING
# ============================================================


class TestConfidence:
    def test_earlier_patterns_higher_confidence(self):
        """First matching pattern should have higher confidence."""
        # Use a text that matches the first patrimonio pattern
        text = "patrimonio liquido minimo de R$ 500.000,00."
        result = extract_structured(text, DocType.EDITAL)
        field = result.fields["patrimonio_liquido"]
        assert field.confidence >= 0.85  # First pattern -> 1.0

    def test_count_processor(self):
        """Planilha num_itens uses count processor."""
        text = "item 1: Concreto. item 2: Aço. item 3: Areia."
        result = extract_structured(text, DocType.PLANILHA)
        field = result.fields["num_itens"]
        assert field.found is True
        assert int(field.value) == 3


# ============================================================
# PLANILHA-SPECIFIC PATTERNS
# ============================================================


class TestPlanilhaPatterns:
    def test_valor_total(self):
        text = "Valor total geral R$ 2.500.000,00."
        result = extract_structured(text, DocType.PLANILHA)
        field = result.fields["valor_total"]
        assert field.found is True
        assert "2.500.000,00" in field.value

    def test_bdi(self):
        text = "BDI aplicado: 25,50%."
        result = extract_structured(text, DocType.PLANILHA)
        field = result.fields["bdi"]
        assert field.found is True
        assert "25,50" in field.value

    def test_encargos_sociais(self):
        text = "Encargos sociais de 68,50% sobre mao de obra."
        result = extract_structured(text, DocType.PLANILHA)
        field = result.fields["encargos_sociais"]
        assert field.found is True
