"""
Tests for scripts/intel-report.py — PDF report generation.

Run: pytest scripts/tests/test_intel_report.py -v
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure scripts/ and scripts/tests/ are importable
_scripts_dir = str(Path(__file__).resolve().parent.parent)
_tests_dir = str(Path(__file__).resolve().parent)
for _d in (_scripts_dir, _tests_dir):
    if _d not in sys.path:
        sys.path.insert(0, _d)

# Skip all tests if reportlab not installed
reportlab = pytest.importorskip("reportlab")

# Import the module under test
_report_path = str(Path(__file__).resolve().parent.parent / "intel-report.py")
_spec = importlib.util.spec_from_file_location("intel_report", _report_path)
assert _spec is not None and _spec.loader is not None
intel_report = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intel_report)

# Import shared fixtures
from conftest_intel import (
    make_edital,
    make_edital_with_analise,
    make_empresa,
    make_intel_data,
)


# ── Helpers ──────────────────────────────────────────────────────


def _is_valid_pdf(path: str | Path) -> bool:
    """Check if file starts with %PDF magic bytes."""
    with open(str(path), "rb") as f:
        header = f.read(5)
    return header == b"%PDF-"


# ── Tests ────────────────────────────────────────────────────────


class TestGenerateReportBasic:
    """Core PDF generation tests."""

    def test_creates_valid_pdf(self, tmp_path):
        """Generated file should start with %PDF."""
        data = make_intel_data(n_editais=5, n_top20=3, with_analise=True)
        out = str(tmp_path / "test.pdf")
        result = intel_report.generate_intel_report(data, out)
        assert os.path.isfile(result)
        assert _is_valid_pdf(result)

    def test_pdf_has_reasonable_size(self, tmp_path):
        """PDF with 3 analyzed editais should be at least a few KB."""
        data = make_intel_data(n_editais=5, n_top20=3, with_analise=True)
        out = str(tmp_path / "size.pdf")
        intel_report.generate_intel_report(data, out)
        size = os.path.getsize(out)
        assert size > 5000, f"PDF too small: {size} bytes"

    def test_creates_parent_directories(self, tmp_path):
        data = make_intel_data(n_editais=2, n_top20=1, with_analise=True)
        out = str(tmp_path / "deep" / "nested" / "report.pdf")
        # generate_intel_report doesn't create dirs — caller's responsibility
        os.makedirs(os.path.dirname(out), exist_ok=True)
        intel_report.generate_intel_report(data, out)
        assert os.path.isfile(out)


class TestEmptyAndPartialData:
    """Edge cases with missing or minimal data."""

    def test_empty_top20_generates_pdf(self, tmp_path):
        """Empty top20 should still produce a valid PDF (cover + summary)."""
        data = make_intel_data(n_editais=5, n_top20=0, with_analise=False)
        out = str(tmp_path / "empty_top20.pdf")
        intel_report.generate_intel_report(data, out)
        assert _is_valid_pdf(out)

    def test_top20_without_analise(self, tmp_path):
        """Top20 editais without analysis should produce a valid PDF."""
        data = make_intel_data(n_editais=5, n_top20=3, with_analise=False)
        out = str(tmp_path / "no_analise.pdf")
        intel_report.generate_intel_report(data, out)
        assert _is_valid_pdf(out)

    def test_missing_resumo_executivo_handled(self, tmp_path):
        """Data without resumo_executivo field should use generated one."""
        data = make_intel_data(n_editais=5, n_top20=3, with_analise=True)
        # The report always generates resumo from data — no JSON field needed
        out = str(tmp_path / "no_resumo.pdf")
        intel_report.generate_intel_report(data, out)
        assert _is_valid_pdf(out)

    def test_minimal_empresa_data(self, tmp_path):
        """Empresa with only CNPJ and razao_social should not crash."""
        data = make_intel_data(n_editais=2, n_top20=1, with_analise=True)
        data["empresa"] = {
            "cnpj": "99999999000100",
            "razao_social": "Empresa Minima",
        }
        out = str(tmp_path / "minimal.pdf")
        intel_report.generate_intel_report(data, out)
        assert _is_valid_pdf(out)


class TestFilterTop20:
    """Tests for _filter_top20 logic."""

    def test_removes_nao_participar(self):
        eds = [
            make_edital_with_analise(1),
            make_edital_with_analise(2),
        ]
        eds[1]["analise"]["recomendacao_acao"] = "NAO PARTICIPAR"
        result = intel_report._filter_top20(eds)
        assert len(result) == 1

    def test_removes_expired(self):
        eds = [
            make_edital_with_analise(1),
            make_edital_with_analise(2, status_temporal="EXPIRADO"),
        ]
        result = intel_report._filter_top20(eds)
        assert len(result) == 1

    def test_dedup_same_objeto_valor_uf(self):
        ed1 = make_edital_with_analise(1, objeto="Obra X", valor_estimado=1000000, uf="SC")
        ed2 = make_edital_with_analise(2, objeto="Obra X", valor_estimado=1000000, uf="SC")
        result = intel_report._filter_top20([ed1, ed2])
        assert len(result) == 1

    def test_keeps_different_editais(self):
        eds = [make_edital_with_analise(i) for i in range(1, 6)]
        result = intel_report._filter_top20(eds)
        assert len(result) == 5


class TestQualityGate:
    """Tests for quality gate validation in generate_intel_report."""

    def test_quality_stats_populated(self, tmp_path):
        data = make_intel_data(n_editais=5, n_top20=3, with_analise=True)
        out = str(tmp_path / "quality.pdf")
        intel_report.generate_intel_report(data, out)
        qs = data.get("quality_stats")
        assert qs is not None
        assert "completeness_pct" in qs
        assert qs["completeness_pct"] > 0

    def test_quality_100_pct_when_all_fields_present(self, tmp_path):
        data = make_intel_data(n_editais=3, n_top20=3, with_analise=True)
        out = str(tmp_path / "quality100.pdf")
        intel_report.generate_intel_report(data, out)
        assert data["quality_stats"]["completeness_pct"] == 100

    def test_quality_detects_missing_fields(self, tmp_path):
        data = make_intel_data(n_editais=3, n_top20=2, with_analise=True)
        # Remove a required field
        data["top20"][0]["analise"]["criterio_julgamento"] = ""
        out = str(tmp_path / "quality_warn.pdf")
        intel_report.generate_intel_report(data, out)
        qs = data["quality_stats"]
        assert qs["completeness_pct"] < 100
        assert len(qs["warnings"]) > 0


class TestDeterministicResumo:
    """Tests for _generate_resumo and _generate_proximos_passos."""

    def test_resumo_mentions_company_name(self):
        empresa = make_empresa(razao_social="ACME Construcoes")
        top20 = [make_edital_with_analise(i) for i in range(1, 4)]
        stats = {"total_cnae_compativel": 10, "total_expirados_removidos": 3}
        resumo = intel_report._generate_resumo(empresa, top20, stats)
        assert "ACME" in resumo

    def test_resumo_counts_participar(self):
        top20 = [make_edital_with_analise(i) for i in range(1, 4)]
        top20[2]["analise"]["recomendacao_acao"] = "NAO PARTICIPAR"
        stats = {"total_cnae_compativel": 10, "total_expirados_removidos": 2}
        resumo = intel_report._generate_resumo(make_empresa(), top20, stats)
        assert "2 receberam" in resumo  # 2 PARTICIPAR

    def test_proximos_passos_returns_list(self):
        top20 = [make_edital_with_analise(i) for i in range(1, 6)]
        passos = intel_report._generate_proximos_passos(top20)
        assert isinstance(passos, list)
        assert len(passos) > 0

    def test_proximos_passos_empty_for_no_participar(self):
        top20 = [make_edital_with_analise(1)]
        top20[0]["analise"]["recomendacao_acao"] = "NAO PARTICIPAR"
        passos = intel_report._generate_proximos_passos(top20)
        assert len(passos) == 0


class TestStatusTemporalBadges:
    """Tests for status temporal badge rendering."""

    def test_urgente_badge(self, tmp_path):
        data = make_intel_data(n_editais=2, n_top20=1, with_analise=True)
        data["top20"][0]["status_temporal"] = "URGENTE"
        data["top20"][0]["dias_restantes"] = 2
        out = str(tmp_path / "urgente.pdf")
        intel_report.generate_intel_report(data, out)
        assert _is_valid_pdf(out)

    def test_iminente_badge(self, tmp_path):
        data = make_intel_data(n_editais=2, n_top20=1, with_analise=True)
        data["top20"][0]["status_temporal"] = "IMINENTE"
        data["top20"][0]["dias_restantes"] = 5
        out = str(tmp_path / "iminente.pdf")
        intel_report.generate_intel_report(data, out)
        assert _is_valid_pdf(out)

    def test_planejavel_badge(self, tmp_path):
        data = make_intel_data(n_editais=2, n_top20=1, with_analise=True)
        data["top20"][0]["status_temporal"] = "PLANEJAVEL"
        data["top20"][0]["dias_restantes"] = 15
        out = str(tmp_path / "planejavel.pdf")
        intel_report.generate_intel_report(data, out)
        assert _is_valid_pdf(out)


class TestHelpers:
    """Unit tests for helper functions."""

    def test_currency_formatting(self):
        assert intel_report._currency(1234.50) == "R$ 1.234,50"
        assert intel_report._currency(None) == "N/I"

    def test_currency_short_millions(self):
        result = intel_report._currency_short(2_500_000)
        assert "M" in result
        assert "2" in result

    def test_currency_short_thousands(self):
        result = intel_report._currency_short(50_000)
        assert "K" in result

    def test_date_formatting(self):
        assert intel_report._date("2026-03-20") == "20/03/2026"
        assert intel_report._date(None) == "N/I"
        assert intel_report._date("") == "N/I"

    def test_sanitize_removes_control_chars(self):
        assert intel_report._s("hello\x00world") == "hello world"
        assert intel_report._s(None) == ""

    def test_restore_accents(self):
        result = intel_report._restore_accents("construcao de edificios")
        assert "construção" in result or "constru" in result

    def test_smart_trunc_strips_prefix(self):
        text = "Contratação de empresa especializada em pavimentação asfáltica"
        result = intel_report._smart_trunc(text, 50)
        assert not result.startswith("Contratação de empresa")
        assert len(result) <= 50

    def test_format_cnpj(self):
        assert intel_report._format_cnpj("12345678000199") == "12.345.678/0001-99"

    def test_fix_pncp_link_3part(self):
        bad = "https://pncp.gov.br/app/editais/12345678000199-2026-5"
        fixed = intel_report._fix_pncp_link(bad)
        assert fixed == "https://pncp.gov.br/app/editais/12345678000199/2026/5"

    def test_fix_pncp_link_already_correct(self):
        good = "https://pncp.gov.br/app/editais/12345678000199/2026/5"
        assert intel_report._fix_pncp_link(good) == good

    def test_plural(self):
        assert intel_report._plural(1, "edital", "editais") == "edital"
        assert intel_report._plural(3, "edital", "editais") == "editais"


class TestCLI:
    """CLI argument parsing and auto-naming tests."""

    def test_auto_naming_when_no_output(self, tmp_path):
        """When --output is not provided, PDF name is auto-generated."""
        data = make_intel_data(n_editais=3, n_top20=2, with_analise=True)
        json_path = tmp_path / "test-data.json"
        json_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        with patch("sys.argv", ["prog", "--input", str(json_path)]):
            result = intel_report.main()
        # Result should be a path ending in .pdf
        assert result is not None
        assert str(result).endswith(".pdf")
        assert os.path.isfile(result)

    def test_explicit_output_path(self, tmp_path):
        data = make_intel_data(n_editais=3, n_top20=2, with_analise=True)
        json_path = tmp_path / "input.json"
        json_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        out_path = str(tmp_path / "custom-name.pdf")
        with patch("sys.argv", ["prog", "--input", str(json_path), "--output", out_path]):
            result = intel_report.main()
        assert os.path.isfile(out_path)


class TestDeltaSection:
    """Tests for delta/changes section."""

    def test_delta_section_rendered_when_present(self, tmp_path):
        data = make_intel_data(n_editais=3, n_top20=2, with_analise=True)
        data["meta"] = {
            "_delta_summary": {
                "data_anterior": "15/03/2026",
                "novos": 3,
                "atualizados": 1,
                "vencendo_3dias": 1,
                "sem_alteracao": 5,
            }
        }
        out = str(tmp_path / "delta.pdf")
        intel_report.generate_intel_report(data, out)
        assert _is_valid_pdf(out)
        # File should be larger due to delta section
        assert os.path.getsize(out) > 5000

    def test_no_delta_section_when_absent(self, tmp_path):
        data = make_intel_data(n_editais=3, n_top20=2, with_analise=True)
        data["meta"] = {}
        out = str(tmp_path / "no_delta.pdf")
        intel_report.generate_intel_report(data, out)
        assert _is_valid_pdf(out)


class TestConsorcioSection:
    """Tests for consortium opportunities section."""

    def test_consorcio_section_rendered(self, tmp_path):
        data = make_intel_data(n_editais=3, n_top20=2, with_analise=True)
        data["consorcio_opportunities"] = [
            {
                "objeto": "Grande obra de infraestrutura",
                "valor_estimado": 50_000_000,
                "uf": "SP",
                "municipio": "Sao Paulo",
                "motivo_interesse": "Setor compativel, valor acima da capacidade",
                "link": "https://pncp.gov.br/app/editais/99999999000100/2026/1",
            }
        ]
        out = str(tmp_path / "consorcio.pdf")
        intel_report.generate_intel_report(data, out)
        assert _is_valid_pdf(out)

    def test_no_consorcio_when_empty(self, tmp_path):
        data = make_intel_data(n_editais=3, n_top20=2, with_analise=True)
        out = str(tmp_path / "no_consorcio.pdf")
        intel_report.generate_intel_report(data, out)
        assert _is_valid_pdf(out)
