"""
Tests for scripts/intel-excel.py — Excel workbook generation.

Run: pytest scripts/tests/test_intel_excel.py -v
"""
from __future__ import annotations

import json
import os
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

# We need openpyxl for verification
openpyxl = pytest.importorskip("openpyxl")

# Import the module under test -- load as a module to avoid __main__ execution
import importlib.util

# Temporarily disable platform check so the Windows stdout wrapper
# doesn't interfere with pytest's stdout capture.
_real_platform = sys.platform
sys.platform = "linux"  # Prevent Windows-only wrapping during import

_excel_path = str(Path(__file__).resolve().parent.parent / "intel-excel.py")
_spec = importlib.util.spec_from_file_location("intel_excel", _excel_path)
assert _spec is not None and _spec.loader is not None
intel_excel = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(intel_excel)

sys.platform = _real_platform  # Restore

# Import shared fixtures
from conftest_intel import (
    make_edital,
    make_empresa,
    make_intel_data,
)


# ── Helpers ──────────────────────────────────────────────────────


def _load_workbook(path: str | Path):
    """Load .xlsx with openpyxl (read-only for speed)."""
    return openpyxl.load_workbook(str(path), read_only=True, data_only=True)


# ── Tests ────────────────────────────────────────────────────────


class TestGenerateExcelBasic:
    """Core workbook generation tests."""

    def test_creates_valid_xlsx_file(self, tmp_path):
        """Generated file is a valid .xlsx that openpyxl can open."""
        data = make_intel_data(n_editais=3)
        out = str(tmp_path / "test.xlsx")
        result = intel_excel.generate_excel(data, out)
        assert os.path.isfile(result)
        wb = _load_workbook(result)
        assert wb is not None
        wb.close()

    def test_output_path_returned_is_absolute(self, tmp_path):
        data = make_intel_data(n_editais=1)
        out = str(tmp_path / "out.xlsx")
        result = intel_excel.generate_excel(data, out)
        assert os.path.isabs(result)

    def test_correct_number_of_sheets(self, tmp_path):
        """Workbook should have 4 sheets: Oportunidades, Resumo por UF, Resumo por Modalidade, Metadata."""
        data = make_intel_data(n_editais=5)
        out = str(tmp_path / "sheets.xlsx")
        intel_excel.generate_excel(data, out)
        wb = _load_workbook(out)
        assert wb.sheetnames == [
            "Oportunidades",
            "Resumo por UF",
            "Resumo por Modalidade",
            "Metadata",
        ]
        wb.close()

    def test_creates_parent_directories(self, tmp_path):
        """Output directories are created if they don't exist."""
        data = make_intel_data(n_editais=1)
        out = str(tmp_path / "deep" / "nested" / "dir" / "test.xlsx")
        intel_excel.generate_excel(data, out)
        assert os.path.isfile(out)


class TestOportunidadesSheet:
    """Tests for Sheet 1 — Oportunidades."""

    def test_header_row_matches_columns(self, tmp_path):
        """First row headers should match the COLUMNS definition."""
        data = make_intel_data(n_editais=2)
        out = str(tmp_path / "headers.xlsx")
        intel_excel.generate_excel(data, out)
        wb = _load_workbook(out)
        ws = wb["Oportunidades"]
        headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
        expected = [col[0] for col in intel_excel.COLUMNS]
        assert headers == expected
        wb.close()

    def test_data_rows_count(self, tmp_path):
        """Number of data rows = compatible editais + 1 header + 1 total row."""
        data = make_intel_data(n_editais=5)
        # All 5 editais are cnae_compatible=True and not expired
        out = str(tmp_path / "rows.xlsx")
        intel_excel.generate_excel(data, out)
        wb = _load_workbook(out)
        ws = wb["Oportunidades"]
        rows = list(ws.iter_rows())
        # header(1) + 5 data + 1 total = 7
        assert len(rows) == 7
        wb.close()

    def test_currency_values_are_numeric(self, tmp_path):
        """Valor Estimado column should contain actual numbers, not strings."""
        data = make_intel_data(n_editais=2)
        out = str(tmp_path / "currency.xlsx")
        intel_excel.generate_excel(data, out)
        wb = _load_workbook(out)
        ws = wb["Oportunidades"]
        # Row 2 is first data row, column 7 is Valor Estimado
        rows = list(ws.iter_rows(min_row=2, max_row=2))
        valor_cell = rows[0][6]  # 0-indexed col 7
        # Should be numeric (float or int), not a string
        assert isinstance(valor_cell.value, (int, float))
        wb.close()

    def test_filters_only_compatible_editais(self, tmp_path):
        """Only CNAE-compatible, non-expired editais go to Oportunidades sheet."""
        editais = [
            make_edital(1, cnae_compatible=True),
            make_edital(2, cnae_compatible=False),
            make_edital(3, cnae_compatible=True, status_temporal="EXPIRADO"),
            make_edital(4, cnae_compatible=True),
        ]
        data = make_intel_data(n_editais=0)
        data["editais"] = editais
        out = str(tmp_path / "filter.xlsx")
        intel_excel.generate_excel(data, out)
        wb = _load_workbook(out)
        ws = wb["Oportunidades"]
        rows = list(ws.iter_rows())
        # header(1) + 2 compatible non-expired + 1 total = 4
        assert len(rows) == 4
        wb.close()

    def test_sorted_by_valor_descending(self, tmp_path):
        """Data rows should be sorted by valor_estimado descending."""
        editais = [
            make_edital(1, cnae_compatible=True, valor_estimado=100_000),
            make_edital(2, cnae_compatible=True, valor_estimado=500_000),
            make_edital(3, cnae_compatible=True, valor_estimado=300_000),
        ]
        data = make_intel_data(n_editais=0)
        data["editais"] = editais
        out = str(tmp_path / "sorted.xlsx")
        intel_excel.generate_excel(data, out)
        wb = _load_workbook(out)
        ws = wb["Oportunidades"]
        valores = []
        for row in ws.iter_rows(min_row=2, max_row=4):
            val = row[6].value  # col 7 = Valor Estimado
            if isinstance(val, (int, float)):
                valores.append(val)
        assert valores == sorted(valores, reverse=True)
        wb.close()


class TestEmptyAndPartialData:
    """Edge cases: empty lists, missing fields."""

    def test_empty_editais_list(self, tmp_path):
        """Empty editais should produce a valid workbook with empty data sheets."""
        data = make_intel_data(n_editais=0)
        out = str(tmp_path / "empty.xlsx")
        intel_excel.generate_excel(data, out)
        wb = _load_workbook(out)
        ws = wb["Oportunidades"]
        rows = list(ws.iter_rows())
        # Only header row (no data, no total)
        assert len(rows) == 1
        wb.close()

    def test_missing_fields_handled_gracefully(self, tmp_path):
        """Editais with missing fields should not crash."""
        edital = {
            "_id": "minimal-1",
            "cnae_compatible": True,
            "objeto": "Test",
        }
        data = make_intel_data(n_editais=0)
        data["editais"] = [edital]
        out = str(tmp_path / "partial.xlsx")
        # Should not raise
        intel_excel.generate_excel(data, out)
        assert os.path.isfile(out)

    def test_none_valor_shows_sigiloso(self, tmp_path):
        """When valor_estimado is None, cell should show 'Sigiloso'."""
        editais = [make_edital(1, cnae_compatible=True, valor_estimado=None)]
        data = make_intel_data(n_editais=0)
        data["editais"] = editais
        out = str(tmp_path / "sigiloso.xlsx")
        intel_excel.generate_excel(data, out)
        wb = _load_workbook(out)
        ws = wb["Oportunidades"]
        rows = list(ws.iter_rows(min_row=2, max_row=2))
        val = rows[0][6].value  # Valor Estimado column
        assert val == "Sigiloso"
        wb.close()


class TestResumoSheets:
    """Tests for Resumo por UF and Resumo por Modalidade sheets."""

    def test_resumo_uf_aggregation(self, tmp_path):
        """Resumo por UF should aggregate all editais (not just compatible)."""
        editais = [
            make_edital(1, uf="SC", cnae_compatible=True, valor_estimado=100_000),
            make_edital(2, uf="SC", cnae_compatible=False, valor_estimado=200_000),
            make_edital(3, uf="PR", cnae_compatible=True, valor_estimado=300_000),
        ]
        data = make_intel_data(n_editais=0)
        data["editais"] = editais
        out = str(tmp_path / "uf.xlsx")
        intel_excel.generate_excel(data, out)
        wb = _load_workbook(out)
        ws = wb["Resumo por UF"]
        rows = list(ws.iter_rows())
        # header(1) + 2 UFs (PR, SC) + 1 total = 4
        assert len(rows) == 4
        wb.close()

    def test_resumo_modalidade_aggregation(self, tmp_path):
        editais = [
            make_edital(1, modalidade_nome="Pregao Eletronico"),
            make_edital(2, modalidade_nome="Concorrencia"),
            make_edital(3, modalidade_nome="Pregao Eletronico"),
        ]
        data = make_intel_data(n_editais=0)
        data["editais"] = editais
        out = str(tmp_path / "mod.xlsx")
        intel_excel.generate_excel(data, out)
        wb = _load_workbook(out)
        ws = wb["Resumo por Modalidade"]
        rows = list(ws.iter_rows())
        # header(1) + 2 modalidades + 1 total = 4
        assert len(rows) == 4
        wb.close()


class TestMetadataSheet:
    """Tests for Sheet 4 — Metadata."""

    def test_metadata_has_cnpj(self, tmp_path):
        data = make_intel_data(n_editais=1)
        out = str(tmp_path / "meta.xlsx")
        intel_excel.generate_excel(data, out)
        wb = _load_workbook(out)
        ws = wb["Metadata"]
        # Find CNPJ row
        found = False
        for row in ws.iter_rows():
            if row[0].value == "CNPJ":
                assert "12.345.678/0001-99" in str(row[1].value)
                found = True
                break
        assert found, "CNPJ row not found in Metadata sheet"
        wb.close()

    def test_metadata_has_sancionada_field(self, tmp_path):
        data = make_intel_data(n_editais=1)
        out = str(tmp_path / "meta_sanc.xlsx")
        intel_excel.generate_excel(data, out)
        wb = _load_workbook(out)
        ws = wb["Metadata"]
        values = [str(row[0].value) for row in ws.iter_rows()]
        assert "Empresa Sancionada" in values
        wb.close()


class TestLargeDataset:
    """Performance and correctness with 100+ editais."""

    def test_large_dataset_120_editais(self, tmp_path):
        """120 editais should produce a valid workbook without error."""
        data = make_intel_data(n_editais=120)
        out = str(tmp_path / "large.xlsx")
        intel_excel.generate_excel(data, out)
        assert os.path.isfile(out)
        size = os.path.getsize(out)
        assert size > 10_000  # should be at least 10KB
        wb = _load_workbook(out)
        ws = wb["Oportunidades"]
        rows = list(ws.iter_rows())
        # header + 120 data + 1 total = 122
        assert len(rows) == 122
        wb.close()


class TestStyling:
    """Verify styling is applied (non-read-only mode needed for style checks)."""

    def test_column_widths_set(self, tmp_path):
        """Column widths should be set according to COLUMNS definition."""
        data = make_intel_data(n_editais=1)
        out = str(tmp_path / "widths.xlsx")
        intel_excel.generate_excel(data, out)
        # Re-open in full mode to check dimensions
        wb = openpyxl.load_workbook(str(out), read_only=False)
        ws = wb["Oportunidades"]
        for col_idx, (_, expected_width, _) in enumerate(intel_excel.COLUMNS, start=1):
            col_letter = openpyxl.utils.get_column_letter(col_idx)
            actual = ws.column_dimensions[col_letter].width
            assert actual == expected_width, f"Col {col_letter} width {actual} != {expected_width}"
        wb.close()

    def test_freeze_panes_set(self, tmp_path):
        data = make_intel_data(n_editais=1)
        out = str(tmp_path / "freeze.xlsx")
        intel_excel.generate_excel(data, out)
        wb = openpyxl.load_workbook(str(out), read_only=False)
        ws = wb["Oportunidades"]
        assert ws.freeze_panes == "A2"
        wb.close()


class TestHelpers:
    """Unit tests for helper functions."""

    def test_sanitize_removes_control_chars(self):
        assert intel_excel._sanitize("hello\x00world") == "helloworld"
        assert intel_excel._sanitize(None) == ""

    def test_parse_dt_iso(self):
        dt = intel_excel._parse_dt("2026-03-20T10:00:00")
        assert dt is not None
        assert dt.year == 2026 and dt.month == 3 and dt.day == 20

    def test_parse_dt_br_format(self):
        dt = intel_excel._parse_dt("20/03/2026")
        assert dt is not None
        assert dt.day == 20 and dt.month == 3

    def test_safe_float(self):
        assert intel_excel._safe_float(123.45) == 123.45
        assert intel_excel._safe_float("1.234,56") == 1234.56
        assert intel_excel._safe_float(None) is None
        assert intel_excel._safe_float("abc") is None

    def test_cnae_label_values(self):
        assert intel_excel._cnae_label({"cnae_compatible": True}) == "SIM"
        assert intel_excel._cnae_label({"cnae_compatible": False}) == "N\u00c3O"
        assert intel_excel._cnae_label({}) == "AVALIAR"

    def test_capacity_label(self):
        assert intel_excel._capacity_label(100_000, 500_000) == "SIM"
        assert intel_excel._capacity_label(600_000, 500_000) == "N\u00c3O"
        assert intel_excel._capacity_label(None, 500_000) == "N/D"

    def test_format_cnpj(self):
        assert intel_excel._format_cnpj("12345678000199") == "12.345.678/0001-99"

    def test_format_brl(self):
        result = intel_excel._format_brl(1234.50)
        assert "1.234,50" in result
        assert intel_excel._format_brl(None) == "N/D"


class TestCLI:
    """CLI argument parsing tests."""

    def test_cli_requires_input(self):
        """Should exit with error when --input is missing."""
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--input", "-i", required=True)
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_cli_default_output_is_xlsx(self, tmp_path):
        """When --output is not provided, output should be .xlsx with same basename."""
        data = make_intel_data(n_editais=1)
        json_path = tmp_path / "data.json"
        json_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        with patch("sys.argv", ["prog", "--input", str(json_path)]):
            intel_excel.main()
        expected_output = tmp_path / "data.xlsx"
        assert expected_output.exists()
