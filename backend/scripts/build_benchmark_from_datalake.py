#!/usr/bin/env python3
"""Build expanded precision/recall benchmark ground truth from datalake.

Queries pncp_raw_bids via Supabase RPC and uses the existing keyword matcher
to auto-label editais as relevant/irrelevant per sector. Then samples a
balanced dataset for manual verification or direct use.

Output: backend/tests/benchmark_ground_truth.json
"""
import json
import os
import re
import sys
from pathlib import Path

# Setup paths
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv(str(Path(__file__).resolve().parent.parent.parent / ".env"))

from supabase import create_client
from sectors import list_sectors, get_sector
from filter.keywords import match_keywords

# Config
SAMPLES_PER_SECTOR_RELEVANT = 50
SAMPLES_PER_SECTOR_IRRELEVANT = 50
OUTPUT_FILE = Path(backend_dir) / "tests" / "benchmark_ground_truth.json"


def fetch_all_editais() -> list[dict]:
    """Fetch all editais from datalake (all UFs, all modalidades)."""
    sb = create_client(
        os.getenv("SUPABASE_URL", ""),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
    )

    all_ufs = [
        "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG",
        "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR",
        "RS", "SC", "SE", "SP", "TO",
    ]

    rows: list[dict] = []
    for uf in all_ufs:
        try:
            result = sb.rpc("search_datalake", {
                "p_ufs": [uf],
                "p_limit": 5000,
            }).execute()
            uf_rows = result.data or []
            rows.extend(uf_rows)
            print(f"  {uf}: {len(uf_rows)} editais")
        except Exception as e:
            print(f"  {uf}: ERRO — {e}")

    print(f"\nTotal: {len(rows)} editais do datalake")
    return rows


def classify_editais(rows: list[dict]) -> dict[str, dict[str, list[str]]]:
    """Classify each edital against all sectors using match_keywords.

    Returns per-sector lists of relevant and irrelevant objeto strings.
    """
    all_sectors = list_sectors()
    sector_ids = [s["id"] for s in all_sectors]

    # Pre-extract unique objetos (dedup)
    objetos: list[str] = []
    seen: set[str] = set()
    for row in rows:
        obj = (row.get("objeto_compra") or "").strip()
        if obj and len(obj) > 30 and obj not in seen:
            seen.add(obj)
            objetos.append(obj)

    print(f"Objetos únicos (>30 chars): {len(objetos)}")

    # Classify each objeto against each sector
    result: dict[str, dict[str, list[str]]] = {}
    for sector_id in sector_ids:
        sector = get_sector(sector_id)
        relevant: list[str] = []
        irrelevant: list[str] = []

        for obj in objetos:
            matched, kws = match_keywords(
                objeto=obj,
                keywords=sector.keywords,
                exclusions=sector.exclusions,
                context_required=sector.context_required_keywords,
            )
            if matched:
                relevant.append(obj)
            else:
                irrelevant.append(obj)

        result[sector_id] = {
            "relevant": relevant,
            "irrelevant": irrelevant,
        }
        print(f"  {sector_id}: {len(relevant)} relevant, {len(irrelevant)} irrelevant")

    return result


def sample_balanced(
    classified: dict[str, dict[str, list[str]]],
    n_relevant: int = SAMPLES_PER_SECTOR_RELEVANT,
    n_irrelevant: int = SAMPLES_PER_SECTOR_IRRELEVANT,
) -> dict[str, dict[str, list[str]]]:
    """Sample balanced subsets for each sector.

    For irrelevant: prioritize near-misses (editais relevant to OTHER sectors)
    over generic irrelevant ones, as near-misses are harder edge cases.
    """
    import random
    random.seed(42)  # Reproducible

    # Build set of relevant per sector for near-miss selection
    sector_relevant_sets: dict[str, set[str]] = {}
    for sid, data in classified.items():
        sector_relevant_sets[sid] = set(data["relevant"])

    sampled: dict[str, dict[str, list[str]]] = {}

    for sid, data in classified.items():
        # Sample relevant
        rel = data["relevant"]
        if len(rel) > n_relevant:
            # Prioritize diversity: spread across object length ranges
            rel_sorted = sorted(rel, key=len)
            step = max(1, len(rel_sorted) // n_relevant)
            rel_sample = rel_sorted[::step][:n_relevant]
        else:
            rel_sample = rel

        # Sample irrelevant: prefer near-misses from other sectors
        irr = data["irrelevant"]
        near_misses: list[str] = []
        generic_irr: list[str] = []

        for obj in irr:
            # Is this relevant to another sector? → near-miss (harder test case)
            is_near_miss = any(
                obj in sector_relevant_sets[other_sid]
                for other_sid in classified
                if other_sid != sid
            )
            if is_near_miss:
                near_misses.append(obj)
            else:
                generic_irr.append(obj)

        # Take up to 70% near-misses, rest generic
        n_near = min(len(near_misses), int(n_irrelevant * 0.7))
        n_generic = min(len(generic_irr), n_irrelevant - n_near)

        irr_sample = (
            random.sample(near_misses, n_near) if n_near > 0 else []
        ) + (
            random.sample(generic_irr, n_generic) if n_generic > 0 else []
        )

        sampled[sid] = {
            "relevant": rel_sample,
            "irrelevant": irr_sample[:n_irrelevant],
            "_stats": {
                "total_relevant": len(data["relevant"]),
                "total_irrelevant": len(data["irrelevant"]),
                "sampled_relevant": len(rel_sample),
                "sampled_irrelevant": len(irr_sample[:n_irrelevant]),
                "near_misses": n_near,
            },
        }

    return sampled


def main():
    print("=== Building benchmark ground truth from datalake ===\n")

    print("[1/3] Fetching editais from datalake...")
    rows = fetch_all_editais()

    if not rows:
        print("ERROR: No editais found in datalake. Run ingestion first.")
        sys.exit(1)

    print(f"\n[2/3] Classifying {len(rows)} editais across 15 sectors...")
    classified = classify_editais(rows)

    print(f"\n[3/3] Sampling balanced dataset ({SAMPLES_PER_SECTOR_RELEVANT} rel + {SAMPLES_PER_SECTOR_IRRELEVANT} irr per sector)...")
    sampled = sample_balanced(classified)

    # Save
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(sampled, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to: {OUTPUT_FILE}")
    print(f"File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")

    # Summary
    total_rel = sum(len(s["relevant"]) for s in sampled.values())
    total_irr = sum(len(s["irrelevant"]) for s in sampled.values())
    print(f"\nTotal: {total_rel} relevant + {total_irr} irrelevant = {total_rel + total_irr} samples")

    for sid, data in sorted(sampled.items()):
        stats = data.get("_stats", {})
        print(f"  {sid}: {stats.get('sampled_relevant', 0)} rel / {stats.get('sampled_irrelevant', 0)} irr "
              f"(near-misses: {stats.get('near_misses', 0)})")


if __name__ == "__main__":
    main()
