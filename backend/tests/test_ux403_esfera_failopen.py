"""
UX-403: Filtro de esfera — fail-open + skip when all selected + stats tracking.

Tests:
- AC1: esferas=["F","E","M"] treated as None (filter skipped)
- AC2: Bid without esferaId included (fail-open) + _esfera_inferred=False
- AC6: stats["esfera_indeterminada"] incremented correctly
"""

import pytest
from filter import aplicar_todos_filtros, filtrar_por_esfera


def _make_bid(esfera_id=None, nome_orgao=None, uf="SP"):
    """Create a minimal bid dict for testing."""
    bid = {
        "uf": uf,
        "dataPublicacao": "2026-03-01",
        "dataAbertura": "2026-03-15",
    }
    if esfera_id is not None:
        bid["esferaId"] = esfera_id
    if nome_orgao is not None:
        bid["nomeOrgao"] = nome_orgao
    return bid


class TestAC1AllEsferasSkipsFilter:
    """AC1: When esferas=["F","E","M"], skip filter entirely."""

    def test_all_three_esferas_returns_same_as_none(self):
        """esferas=["F","E","M"] should produce same esfera stats as esferas=None."""
        bids = [
            _make_bid(esfera_id="F"),
            _make_bid(esfera_id="E"),
            _make_bid(esfera_id="M"),
            _make_bid(nome_orgao="Empresa desconhecida"),
        ]
        _, stats_all = aplicar_todos_filtros(
            bids, ufs_selecionadas={"SP"}, esferas=["F", "E", "M"]
        )
        _, stats_none = aplicar_todos_filtros(
            bids, ufs_selecionadas={"SP"}, esferas=None
        )
        assert stats_all["rejeitadas_esfera"] == stats_none["rejeitadas_esfera"] == 0
        assert stats_all["esfera_indeterminada"] == stats_none["esfera_indeterminada"] == 0

    def test_all_three_esferas_lowercase(self):
        """Lowercase ["f","e","m"] should also skip filter."""
        bids = [
            _make_bid(esfera_id="F"),
            _make_bid(nome_orgao="Entidade qualquer"),
        ]
        _, stats = aplicar_todos_filtros(
            bids, ufs_selecionadas={"SP"}, esferas=["f", "e", "m"]
        )
        assert stats["rejeitadas_esfera"] == 0
        assert stats["esfera_indeterminada"] == 0

    def test_all_three_esferas_mixed_case(self):
        """Mixed case ["F","e","M"] should also skip filter."""
        bids = [
            _make_bid(esfera_id="E"),
            _make_bid(nome_orgao="Orgao sem classificacao"),
        ]
        _, stats = aplicar_todos_filtros(
            bids, ufs_selecionadas={"SP"}, esferas=["F", "e", "M"]
        )
        assert stats["rejeitadas_esfera"] == 0
        assert stats["esfera_indeterminada"] == 0

    def test_subset_still_applies_filter(self):
        """Subset like ["F","E"] should still apply the filter."""
        bids = [
            _make_bid(esfera_id="M"),
            _make_bid(nome_orgao="Entidade desconhecida"),
        ]
        _, stats = aplicar_todos_filtros(
            bids, ufs_selecionadas={"SP"}, esferas=["F", "E"]
        )
        # M bid has known esferaId="M" not in ["F","E"] -> rejected
        assert stats["rejeitadas_esfera"] == 1
        # Unknown org has no esferaId -> fail-open -> indeterminate
        assert stats["esfera_indeterminada"] == 1


class TestAC2FailOpenUndeterminedSphere:
    """AC2: Bids with undetermined sphere are included (fail-open)."""

    def test_undetermined_esfera_not_rejected(self):
        """Bid without esferaId and without keyword match should NOT be rejected."""
        bids = [
            _make_bid(esfera_id="F"),
            _make_bid(nome_orgao="Entidade XYZ"),
        ]
        _, stats = aplicar_todos_filtros(
            bids, ufs_selecionadas={"SP"}, esferas=["F"]
        )
        # fail-open: no rejections, 1 indeterminate
        assert stats["rejeitadas_esfera"] == 0
        assert stats["esfera_indeterminada"] == 1

    def test_esfera_inferred_field_set_on_bid(self):
        """Undetermined bid should have _esfera_inferred=False set on the dict."""
        bid = _make_bid(nome_orgao="Empresa sem classificacao")
        bids = [bid]
        aplicar_todos_filtros(
            bids, ufs_selecionadas={"SP"}, esferas=["F"]
        )
        # The bid object is mutated in-place
        assert bid.get("_esfera_inferred") is False

    def test_known_esfera_no_inferred_field(self):
        """Bid with known esferaId should NOT have _esfera_inferred field."""
        bid = _make_bid(esfera_id="F")
        bids = [bid]
        aplicar_todos_filtros(
            bids, ufs_selecionadas={"SP"}, esferas=["F"]
        )
        assert "_esfera_inferred" not in bid

    def test_keyword_match_no_inferred_field(self):
        """Bid matched by keyword should NOT have _esfera_inferred field."""
        bid = _make_bid(nome_orgao="Ministerio da Saude")
        bids = [bid]
        aplicar_todos_filtros(
            bids, ufs_selecionadas={"SP"}, esferas=["F"]
        )
        assert "_esfera_inferred" not in bid

    def test_fail_open_does_not_increment_rejeitadas(self):
        """Fail-open bids should NOT increment rejeitadas_esfera."""
        bids = [
            _make_bid(nome_orgao="Entidade desconhecida"),
        ]
        _, stats = aplicar_todos_filtros(
            bids, ufs_selecionadas={"SP"}, esferas=["M"]
        )
        assert stats["rejeitadas_esfera"] == 0

    def test_multiple_undetermined_bids(self):
        """Multiple undetermined bids all get fail-open treatment."""
        bids = [
            _make_bid(nome_orgao="Org A"),
            _make_bid(nome_orgao="Org B"),
            _make_bid(nome_orgao="Org C"),
        ]
        _, stats = aplicar_todos_filtros(
            bids, ufs_selecionadas={"SP"}, esferas=["F"]
        )
        assert stats["rejeitadas_esfera"] == 0
        assert stats["esfera_indeterminada"] == 3
        # All bids should have _esfera_inferred set
        for bid in bids:
            assert bid.get("_esfera_inferred") is False


class TestAC6EsferaIndeterminadaStats:
    """AC6: stats['esfera_indeterminada'] tracking."""

    def test_indeterminada_count_zero_when_all_have_esfera(self):
        """No indeterminate count when all bids have known spheres."""
        bids = [
            _make_bid(esfera_id="F"),
            _make_bid(esfera_id="E"),
        ]
        _, stats = aplicar_todos_filtros(
            bids, ufs_selecionadas={"SP"}, esferas=["F", "E"]
        )
        assert stats["esfera_indeterminada"] == 0

    def test_indeterminada_count_incremented(self):
        """Count should reflect number of undetermined bids."""
        bids = [
            _make_bid(esfera_id="F"),
            _make_bid(nome_orgao="Org A"),
            _make_bid(nome_orgao="Org B"),
        ]
        _, stats = aplicar_todos_filtros(
            bids, ufs_selecionadas={"SP"}, esferas=["F"]
        )
        assert stats["esfera_indeterminada"] == 2

    def test_indeterminada_zero_when_filter_skipped(self):
        """When all esferas selected (filter skipped), no indeterminada counted."""
        bids = [
            _make_bid(nome_orgao="Unknown org"),
        ]
        _, stats = aplicar_todos_filtros(
            bids, ufs_selecionadas={"SP"}, esferas=["F", "E", "M"]
        )
        assert stats["esfera_indeterminada"] == 0

    def test_indeterminada_zero_when_none(self):
        """When esferas=None (no filter), no indeterminada counted."""
        bids = [
            _make_bid(nome_orgao="Unknown org"),
        ]
        _, stats = aplicar_todos_filtros(
            bids, ufs_selecionadas={"SP"}, esferas=None
        )
        assert stats["esfera_indeterminada"] == 0

    def test_keyword_match_not_counted_as_indeterminada(self):
        """Bids matched by keyword fallback are NOT indeterminate."""
        bids = [
            _make_bid(nome_orgao="Prefeitura de Sao Paulo"),
        ]
        _, stats = aplicar_todos_filtros(
            bids, ufs_selecionadas={"SP"}, esferas=["M"]
        )
        assert stats["esfera_indeterminada"] == 0

    def test_stats_key_always_present(self):
        """esfera_indeterminada key always present in stats dict."""
        bids = [_make_bid(esfera_id="F")]
        _, stats = aplicar_todos_filtros(
            bids, ufs_selecionadas={"SP"}
        )
        assert "esfera_indeterminada" in stats
