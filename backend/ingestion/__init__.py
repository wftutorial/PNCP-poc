"""PNCP Data Lake ingestion package.

Exports the core functions for crawling PNCP data and loading it
into the pncp_raw_bids table via Supabase RPC.
"""

from .crawler import crawl_full, crawl_incremental
from .transformer import transform_pncp_item
from .loader import bulk_upsert

__all__ = [
    "crawl_full",
    "crawl_incremental",
    "transform_pncp_item",
    "bulk_upsert",
]
