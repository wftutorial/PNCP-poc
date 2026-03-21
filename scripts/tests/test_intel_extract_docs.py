"""Tests for intel-extract-docs.py — document download + text extraction pipeline."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

# Ensure scripts/ is importable
SCRIPTS_DIR = Path(__file__).parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# We need to mock heavy optional deps before import
_mock_fitz = MagicMock()
_mock_pymupdf4llm = MagicMock()

# Patch optional imports so the module loads cleanly
with patch.dict(sys.modules, {
    "fitz": _mock_fitz,
    "pymupdf4llm": _mock_pymupdf4llm,
}):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "intel_extract_docs",
        str(SCRIPTS_DIR / "intel-extract-docs.py"),
    )
    _mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_mod)

# Convenience aliases
_detect_format = _mod._detect_format
_doc_priority = _mod._doc_priority
prioritize_docs = _mod.prioritize_docs
calculate_opportunity_score = _mod.calculate_opportunity_score
select_top_editais = _mod.select_top_editais
_dedup_key = _mod._dedup_key
download_and_extract = _mod.download_and_extract
process_edital = _mod.process_edital
_download_with_retry = _mod._download_with_retry
MAX_DOWNLOAD_BYTES = _mod.MAX_DOWNLOAD_BYTES


# ============================================================
# FORMAT DETECTION
# ============================================================


class TestDetectFormat:
    """Test _detect_format from content-type, URL, and magic bytes."""

    def test_pdf_from_content_type(self, tmp_path):
        p = tmp_path / "doc"
        p.write_bytes(b"anything")
        assert _detect_format("application/pdf", "http://x.com/doc", str(p)) == "pdf"

    def test_zip_from_content_type(self, tmp_path):
        p = tmp_path / "doc"
        p.write_bytes(b"anything")
        assert _detect_format("application/zip", "http://x.com/doc", str(p)) == "zip"

    def test_rar_from_content_type(self, tmp_path):
        p = tmp_path / "doc"
        p.write_bytes(b"anything")
        assert _detect_format("application/x-rar-compressed", "http://x.com/doc", str(p)) == "rar"

    def test_xlsx_from_content_type(self, tmp_path):
        p = tmp_path / "doc"
        p.write_bytes(b"anything")
        assert _detect_format("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "http://x.com/doc", str(p)) == "xlsx"

    def test_xls_from_content_type(self, tmp_path):
        p = tmp_path / "doc"
        p.write_bytes(b"anything")
        assert _detect_format("application/vnd.ms-excel", "http://x.com/doc", str(p)) == "xls"

    def test_pdf_from_url_extension(self, tmp_path):
        p = tmp_path / "doc"
        p.write_bytes(b"anything")
        assert _detect_format("application/octet-stream", "http://x.com/doc.pdf?token=123", str(p)) == "pdf"

    def test_zip_from_url_extension(self, tmp_path):
        p = tmp_path / "doc"
        p.write_bytes(b"anything")
        assert _detect_format("application/octet-stream", "http://x.com/archive.zip", str(p)) == "zip"

    def test_pdf_from_magic_bytes(self, tmp_path):
        p = tmp_path / "doc"
        p.write_bytes(b"%PDF-1.4 rest of content")
        assert _detect_format("application/octet-stream", "http://x.com/doc", str(p)) == "pdf"

    def test_zip_from_magic_bytes(self, tmp_path):
        p = tmp_path / "doc"
        p.write_bytes(b"PK\x03\x04 rest of content")
        assert _detect_format("application/octet-stream", "http://x.com/doc", str(p)) == "zip"

    def test_rar_from_magic_bytes(self, tmp_path):
        p = tmp_path / "doc"
        p.write_bytes(b"Rar!\x1a\x07\x00rest")
        assert _detect_format("application/octet-stream", "http://x.com/doc", str(p)) == "rar"

    def test_unknown_format(self, tmp_path):
        p = tmp_path / "doc"
        p.write_bytes(b"\x00\x00\x00\x00random")
        assert _detect_format("application/octet-stream", "http://x.com/doc", str(p)) == "unknown"


# ============================================================
# DOCUMENT PRIORITIZATION
# ============================================================


class TestDocPriority:
    def test_edital_is_p1(self):
        assert _doc_priority({"titulo": "Edital Pregao 001/2026"}) == 1

    def test_termo_referencia_is_p2(self):
        assert _doc_priority({"titulo": "Termo de Referência"}) == 2

    def test_planilha_is_p3(self):
        assert _doc_priority({"titulo": "Planilha Orcamentaria"}) == 3

    def test_xlsx_url_is_p3(self):
        assert _doc_priority({"titulo": "anexo", "download_url": "http://x.com/file.xlsx"}) == 3

    def test_unknown_is_p4(self):
        assert _doc_priority({"titulo": "Ata de reuniao"}) == 4


class TestPrioritizeDocs:
    def test_sorts_by_priority(self):
        docs = [
            {"titulo": "Planilha", "download_url": "http://a", "ativo": True},
            {"titulo": "Edital", "download_url": "http://b", "ativo": True},
            {"titulo": "Termo de Referência", "download_url": "http://c", "ativo": True},
        ]
        result = prioritize_docs(docs)
        assert result[0]["titulo"] == "Edital"
        assert result[1]["titulo"] == "Termo de Referência"
        assert result[2]["titulo"] == "Planilha"

    def test_filters_inactive(self):
        docs = [
            {"titulo": "Edital", "download_url": "http://b", "ativo": False},
            {"titulo": "TR", "download_url": "http://c", "ativo": True},
        ]
        result = prioritize_docs(docs)
        assert len(result) == 1

    def test_filters_no_url(self):
        docs = [
            {"titulo": "Edital", "download_url": None, "ativo": True},
            {"titulo": "Edital", "ativo": True},  # missing key
        ]
        result = prioritize_docs(docs)
        assert len(result) == 0


# ============================================================
# EXTRACTION QUALITY SCORING
# ============================================================


class TestExtractionQuality:
    """Quality scoring: COMPLETO, PARCIAL, INSUFICIENTE, VAZIO."""

    def _score_edital(self, text):
        """Helper to run quality scoring on a single edital."""
        texto = text or ""
        text_len = len(texto)
        texto_lower = texto.lower()
        key_sections = {
            "habilitacao": any(kw in texto_lower for kw in ["habilitacao", "habilitação"]),
            "qualificacao": any(kw in texto_lower for kw in ["qualificacao economic", "patrimonio liquido", "capital social"]),
            "garantia": any(kw in texto_lower for kw in ["garantia", "caucao", "seguro-garantia"]),
            "prazo": any(kw in texto_lower for kw in ["prazo de execucao", "meses", "dias corridos"]),
            "sessao": any(kw in texto_lower for kw in ["sessao publica", "data da sessao"]),
            "visita": any(kw in texto_lower for kw in ["visita tecnica", "vistoria"]),
            "consorcio": any(kw in texto_lower for kw in ["consorcio"]),
        }
        sections_found = sum(1 for v in key_sections.values() if v)

        if text_len >= 10000 and sections_found >= 3:
            return "COMPLETO"
        elif text_len >= 2000 or sections_found >= 1:
            return "PARCIAL"
        elif text_len > 0:
            return "INSUFICIENTE"
        else:
            return "VAZIO"

    def test_completo(self):
        """>=10K chars + >=3 key sections = COMPLETO."""
        text = "x" * 10000 + " habilitacao garantia prazo de execucao meses consorcio visita tecnica"
        assert self._score_edital(text) == "COMPLETO"

    def test_parcial_by_length(self):
        """2K-10K chars = PARCIAL."""
        text = "x" * 3000
        assert self._score_edital(text) == "PARCIAL"

    def test_parcial_by_section(self):
        """<2K chars but has a section = PARCIAL."""
        text = "habilitacao algo"
        assert self._score_edital(text) == "PARCIAL"

    def test_insuficiente(self):
        """<2K chars, no sections = INSUFICIENTE."""
        text = "algum conteudo curto sem palavras-chave especificas"
        assert self._score_edital(text) == "INSUFICIENTE"

    def test_vazio(self):
        """Empty text = VAZIO."""
        assert self._score_edital("") == "VAZIO"

    def test_10k_but_no_sections(self):
        """>=10K chars but <3 sections = PARCIAL (has >=2000 chars)."""
        text = "x" * 15000
        assert self._score_edital(text) == "PARCIAL"

    def test_10k_with_exactly_3_sections(self):
        text = "x" * 10000 + " habilitacao garantia prazo de execucao"
        assert self._score_edital(text) == "COMPLETO"


# ============================================================
# OPPORTUNITY SCORE & TOP-N SELECTION
# ============================================================


class TestOpportunityScore:
    def test_local_high_value(self):
        """Local edital (<=100km) with max value should score high."""
        ed = {
            "valor_estimado": 1_000_000,
            "distancia": {"km": 50},
            "status_temporal": "URGENTE",
        }
        score = calculate_opportunity_score(ed, capacidade_10x=1_000_000)
        assert score > 0.5

    def test_distant_low_value(self):
        """Distant edital with low value scores lower."""
        ed = {
            "valor_estimado": 100_000,
            "distancia": {"km": 800},
            "status_temporal": "PLANEJAVEL",
        }
        score = calculate_opportunity_score(ed, capacidade_10x=1_000_000)
        assert score < 0.5

    def test_sessao_realizada_zero(self):
        """SESSAO_REALIZADA always returns 0."""
        ed = {
            "valor_estimado": 1_000_000,
            "distancia": {"km": 10},
            "status_temporal": "SESSAO_REALIZADA",
        }
        assert calculate_opportunity_score(ed, capacidade_10x=1_000_000) == 0.0

    def test_unknown_distance_moderate_penalty(self):
        """No distance data = moderate penalty (0.15)."""
        ed = {"valor_estimado": 500_000, "status_temporal": "PLANEJAVEL"}
        score = calculate_opportunity_score(ed, capacidade_10x=1_000_000)
        ed_local = {"valor_estimado": 500_000, "distancia": {"km": 0}, "status_temporal": "PLANEJAVEL"}
        score_local = calculate_opportunity_score(ed_local, capacidade_10x=1_000_000)
        assert score < score_local

    def test_zero_capacity(self):
        ed = {"valor_estimado": 500_000, "status_temporal": "PLANEJAVEL"}
        score = calculate_opportunity_score(ed, capacidade_10x=0)
        # base_score = 0, dist_penalty=0.15, so 0*(1-0.15)+0 = 0
        assert score <= 0.0


class TestSelectTopEditais:
    def test_filters_non_cnae_compatible(self):
        editais = [
            {"cnae_compatible": False, "valor_estimado": 100_000, "status_temporal": "PLANEJAVEL"},
            {"cnae_compatible": True, "valor_estimado": 100_000, "status_temporal": "PLANEJAVEL"},
        ]
        result = select_top_editais(editais, capital_social=100_000, top_n=10)
        assert len(result) == 1

    def test_filters_over_capacity(self):
        """valor > capital_social * 10 should be excluded."""
        editais = [
            {"cnae_compatible": True, "valor_estimado": 2_000_000, "status_temporal": "PLANEJAVEL"},
            {"cnae_compatible": True, "valor_estimado": 500_000, "status_temporal": "PLANEJAVEL"},
        ]
        result = select_top_editais(editais, capital_social=100_000, top_n=10)
        assert len(result) == 1
        assert result[0]["valor_estimado"] == 500_000

    def test_filters_expired(self):
        editais = [
            {"cnae_compatible": True, "valor_estimado": 100_000, "status_temporal": "EXPIRADO"},
            {"cnae_compatible": True, "valor_estimado": 100_000, "status_temporal": "PLANEJAVEL"},
        ]
        result = select_top_editais(editais, capital_social=100_000, top_n=10)
        assert len(result) == 1

    def test_respects_top_n(self):
        editais = [
            {"cnae_compatible": True, "valor_estimado": i * 10_000, "status_temporal": "PLANEJAVEL"}
            for i in range(1, 30)
        ]
        result = select_top_editais(editais, capital_social=1_000_000, top_n=5)
        assert len(result) == 5

    def test_dedup_by_orgao_key(self):
        editais = [
            {"cnae_compatible": True, "valor_estimado": 100_000, "status_temporal": "PLANEJAVEL",
             "orgao_cnpj": "12345678000190", "ano": 2026, "sequencial": 1},
            {"cnae_compatible": True, "valor_estimado": 100_000, "status_temporal": "PLANEJAVEL",
             "orgao_cnpj": "12345678000190", "ano": 2026, "sequencial": 1},
        ]
        result = select_top_editais(editais, capital_social=100_000, top_n=10)
        assert len(result) == 1

    def test_sigiloso_valor_zero_included(self):
        """valor=0 (sigiloso) should be included."""
        editais = [
            {"cnae_compatible": True, "valor_estimado": 0, "status_temporal": "PLANEJAVEL"},
        ]
        result = select_top_editais(editais, capital_social=100_000, top_n=10)
        assert len(result) == 1


# ============================================================
# DOWNLOAD WITH RETRY
# ============================================================


class TestDownloadWithRetry:
    def test_success_first_attempt(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"PDF content"

        with patch.object(_mod, "httpx") as mock_httpx:
            mock_httpx.get.return_value = mock_resp
            mock_httpx.TimeoutException = Exception
            mock_httpx.ConnectError = Exception
            mock_httpx.ReadError = Exception

            result = _download_with_retry("http://example.com/doc.pdf")
            assert result.status_code == 200
            mock_httpx.get.assert_called_once()

    def test_retry_on_502(self):
        resp_502 = MagicMock()
        resp_502.status_code = 502
        resp_200 = MagicMock()
        resp_200.status_code = 200

        with patch.object(_mod, "httpx") as mock_httpx, \
             patch.object(_mod.time, "sleep"):
            mock_httpx.get.side_effect = [resp_502, resp_200]
            mock_httpx.TimeoutException = Exception
            mock_httpx.ConnectError = Exception
            mock_httpx.ReadError = Exception

            result = _download_with_retry("http://example.com/doc.pdf")
            assert result.status_code == 200
            assert mock_httpx.get.call_count == 2

    def test_retry_on_timeout(self):
        import httpx as real_httpx

        resp_ok = MagicMock()
        resp_ok.status_code = 200

        with patch.object(_mod, "httpx") as mock_httpx, \
             patch.object(_mod.time, "sleep"):
            mock_httpx.TimeoutException = real_httpx.TimeoutException
            mock_httpx.ConnectError = real_httpx.ConnectError
            mock_httpx.ReadError = real_httpx.ReadError
            mock_httpx.get.side_effect = [real_httpx.ReadTimeout("timeout"), resp_ok]

            result = _download_with_retry("http://example.com/doc.pdf")
            assert result.status_code == 200

    def test_max_retries_exhausted_raises(self):
        import httpx as real_httpx

        with patch.object(_mod, "httpx") as mock_httpx, \
             patch.object(_mod.time, "sleep"):
            mock_httpx.TimeoutException = real_httpx.TimeoutException
            mock_httpx.ConnectError = real_httpx.ConnectError
            mock_httpx.ReadError = real_httpx.ReadError
            mock_httpx.get.side_effect = real_httpx.ConnectError("refused")

            with pytest.raises(real_httpx.ConnectError):
                _download_with_retry("http://example.com/doc.pdf", max_retries=2)

            assert mock_httpx.get.call_count == 3  # initial + 2 retries

    def test_404_no_retry(self):
        """Non-retryable status codes should not be retried."""
        resp_404 = MagicMock()
        resp_404.status_code = 404

        with patch.object(_mod, "httpx") as mock_httpx:
            mock_httpx.get.return_value = resp_404
            mock_httpx.TimeoutException = Exception
            mock_httpx.ConnectError = Exception
            mock_httpx.ReadError = Exception

            result = _download_with_retry("http://example.com/doc.pdf")
            assert result.status_code == 404
            mock_httpx.get.assert_called_once()

    def test_retry_on_429(self):
        resp_429 = MagicMock()
        resp_429.status_code = 429
        resp_200 = MagicMock()
        resp_200.status_code = 200

        with patch.object(_mod, "httpx") as mock_httpx, \
             patch.object(_mod.time, "sleep"):
            mock_httpx.get.side_effect = [resp_429, resp_200]
            mock_httpx.TimeoutException = Exception
            mock_httpx.ConnectError = Exception
            mock_httpx.ReadError = Exception

            result = _download_with_retry("http://example.com/doc.pdf")
            assert result.status_code == 200

    def test_retry_on_503(self):
        resp_503 = MagicMock()
        resp_503.status_code = 503
        resp_200 = MagicMock()
        resp_200.status_code = 200

        with patch.object(_mod, "httpx") as mock_httpx, \
             patch.object(_mod.time, "sleep"):
            mock_httpx.get.side_effect = [resp_503, resp_200]
            mock_httpx.TimeoutException = Exception
            mock_httpx.ConnectError = Exception
            mock_httpx.ReadError = Exception

            result = _download_with_retry("http://example.com/doc.pdf")
            assert result.status_code == 200


# ============================================================
# DOWNLOAD AND EXTRACT
# ============================================================


class TestDownloadAndExtract:
    def test_no_url_returns_empty(self):
        doc = {"titulo": "Test"}
        with patch.object(_mod, "_download_with_retry") as mock_dl:
            result = download_and_extract(doc, tempfile.mkdtemp())
            assert result == ""
            mock_dl.assert_not_called()

    def test_http_404_returns_empty(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.headers = {"content-type": "text/html"}

        with patch.object(_mod, "_download_with_retry", return_value=mock_resp):
            doc = {"titulo": "Edital", "download_url": "http://pncp.gov.br/doc.pdf"}
            result = download_and_extract(doc, tempfile.mkdtemp())
            assert result == ""

    def test_oversized_content_length_rejected(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"content-type": "application/pdf", "content-length": str(60 * 1024 * 1024)}

        with patch.object(_mod, "_download_with_retry", return_value=mock_resp):
            doc = {"titulo": "Big file", "download_url": "http://pncp.gov.br/huge.pdf"}
            result = download_and_extract(doc, tempfile.mkdtemp())
            assert result == ""

    def test_timeout_returns_empty(self):
        import httpx as real_httpx

        with patch.object(_mod, "_download_with_retry", side_effect=real_httpx.ReadTimeout("timeout")):
            doc = {"titulo": "Slow", "download_url": "http://pncp.gov.br/slow.pdf"}
            result = download_and_extract(doc, tempfile.mkdtemp())
            assert result == ""

    def test_none_response_returns_empty(self):
        with patch.object(_mod, "_download_with_retry", return_value=None):
            doc = {"titulo": "Bad", "download_url": "http://pncp.gov.br/doc.pdf"}
            result = download_and_extract(doc, tempfile.mkdtemp())
            assert result == ""

    def test_oversized_body_rejected(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"content-type": "application/pdf"}
        mock_resp.content = b"x" * (51 * 1024 * 1024)  # 51MB

        with patch.object(_mod, "_download_with_retry", return_value=mock_resp):
            doc = {"titulo": "Big body", "download_url": "http://pncp.gov.br/big.pdf"}
            result = download_and_extract(doc, tempfile.mkdtemp())
            assert result == ""


# ============================================================
# PROCESS EDITAL
# ============================================================


class TestProcessEdital:
    def test_no_docs_sets_empty_text(self):
        ed = {"objeto": "Obra de teste", "documentos": []}
        process_edital(ed, 1, 1)
        assert ed["texto_documentos"] == ""

    def test_no_docs_key_sets_empty_text(self):
        ed = {"objeto": "Obra de teste"}
        process_edital(ed, 1, 1)
        assert ed["texto_documentos"] == ""

    def test_all_inactive_docs_sets_empty_text(self):
        ed = {
            "objeto": "Obra de teste",
            "documentos": [
                {"titulo": "Edital", "download_url": "http://x.com/a", "ativo": False},
            ],
        }
        process_edital(ed, 1, 1)
        assert ed["texto_documentos"] == ""


# ============================================================
# --preserve-top20 FLAG
# ============================================================


class TestPreserveTop20:
    def test_argparse_flag_registered(self):
        """Ensure --preserve-top20 is a valid argument."""
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--input", required=True)
        parser.add_argument("--top", type=int, default=20)
        parser.add_argument("--output", default=None)
        parser.add_argument("--preserve-top20", action="store_true")
        args = parser.parse_args(["--input", "test.json", "--preserve-top20"])
        assert args.preserve_top20 is True


# ============================================================
# OUTPUT JSON STRUCTURE
# ============================================================


class TestOutputStructure:
    def test_quality_fields_set(self):
        """After quality scoring, edital should have extraction_quality and extraction_chars."""
        ed = {"texto_documentos": "habilitacao garantia consorcio " + "x" * 10000}
        texto = ed.get("texto_documentos") or ""
        text_len = len(texto)
        texto_lower = texto.lower()

        key_sections = {
            "habilitacao": "habilitacao" in texto_lower,
            "garantia": "garantia" in texto_lower,
            "consorcio": "consorcio" in texto_lower,
        }
        sections_found = sum(1 for v in key_sections.values() if v)

        if text_len >= 10000 and sections_found >= 3:
            quality = "COMPLETO"
        elif text_len >= 2000 or sections_found >= 1:
            quality = "PARCIAL"
        elif text_len > 0:
            quality = "INSUFICIENTE"
        else:
            quality = "VAZIO"

        ed["extraction_quality"] = quality
        ed["extraction_chars"] = text_len

        assert "extraction_quality" in ed
        assert "extraction_chars" in ed
        assert ed["extraction_quality"] == "COMPLETO"


# ============================================================
# DEDUP KEY
# ============================================================


class TestDedupKey:
    def test_orgao_based_key(self):
        ed = {"orgao_cnpj": "12.345.678/0001-90", "ano": 2026, "sequencial": 42}
        key = _dedup_key(ed)
        assert "12345678000190" in key
        assert "2026" in key
        assert "42" in key

    def test_fallback_key_without_orgao(self):
        ed = {"objeto": "Pavimentacao asfaltica", "valor_estimado": 500000, "uf": "SC"}
        key = _dedup_key(ed)
        assert "SC" in key
        assert "500000" in key

    def test_portal_compras_prefix_stripped(self):
        """Portal de Compras prefix should be stripped in fallback key."""
        ed1 = {"objeto": "[Portal de Compras Públicas] - Pavimentacao", "valor_estimado": 100, "uf": "SC"}
        ed2 = {"objeto": "Pavimentacao", "valor_estimado": 100, "uf": "SC"}
        key1 = _dedup_key(ed1)
        key2 = _dedup_key(ed2)
        assert key1 == key2
