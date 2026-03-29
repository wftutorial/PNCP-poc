"""Stage 5.5: Post-Filter LLM Re-classification — sector relevance gate.

ISSUE-029 + ISSUE-039 fix: After filtering and enrichment, use GPT-4.1-nano
to verify if each approved result is PRIMARILY about the searched sector.

The AI summary LLM already correctly identifies relevant vs irrelevant results
(e.g., "6 relevant" out of 20 for Vestuário). This stage applies the same
intelligence per-item to set accurate confidence badges.

Only runs for sectors with ambiguous keywords (vestuario, saude, etc.).
"""

import asyncio
import logging
import os

from search_context import SearchContext

logger = logging.getLogger(__name__)

# Sectors with ambiguous keywords that need LLM re-classification
_SECTORS_REQUIRING_RECHECK = {
    "vestuario",
    "saude",
}

_MODEL = os.getenv("LLM_ARBITER_MODEL", "gpt-4.1-nano")
_TIMEOUT = float(os.getenv("POST_FILTER_LLM_TIMEOUT_S", "5"))
_MAX_CONCURRENT = 10


async def stage_post_filter_llm(pipeline, ctx: SearchContext) -> None:
    """Re-classify confidence for sectors with ambiguous keywords."""
    if not ctx.licitacoes_filtradas:
        return

    # Only run for ambiguous sectors
    sector_id = ctx.sector.id if ctx.sector else None
    if not sector_id or sector_id not in _SECTORS_REQUIRING_RECHECK:
        return

    sector_name = ctx.sector.name if ctx.sector else "desconhecido"
    total = len(ctx.licitacoes_filtradas)

    logger.info(
        f"Post-filter LLM: re-classifying {total} results for sector '{sector_name}'"
    )

    # Only re-classify keyword-sourced items (LLM-sourced already went through LLM)
    items_to_check = [
        (i, lic) for i, lic in enumerate(ctx.licitacoes_filtradas)
        if lic.get("_relevance_source") == "keyword"
    ]

    if not items_to_check:
        logger.debug("Post-filter LLM: no keyword-sourced items to re-classify")
        return

    try:
        from llm_arbiter import _get_client
        client = _get_client()
    except Exception as e:
        logger.warning(f"Post-filter LLM: client init failed, skipping: {e}")
        return

    sem = asyncio.Semaphore(_MAX_CONCURRENT)
    reclassified = 0

    async def _classify_one(idx: int, lic: dict) -> None:
        nonlocal reclassified
        objeto = (lic.get("objetoCompra") or "")[:500]
        if not objeto:
            return

        prompt = (
            f"A licitação abaixo é PRIMARIAMENTE sobre o setor de {sector_name}? "
            f"Responda APENAS 'SIM' ou 'NAO'. "
            f"Se o objeto principal é de outro setor (limpeza, engenharia, saúde, coleta de resíduos, etc.) "
            f"e apenas menciona itens de {sector_name} como detalhe secundário, responda NAO.\n\n"
            f"Objeto: {objeto}"
        )

        async with sem:
            try:
                response = await asyncio.to_thread(
                    lambda: client.chat.completions.create(
                        model=_MODEL,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0,
                        max_tokens=10,
                        timeout=_TIMEOUT,
                    )
                )
                answer = (response.choices[0].message.content or "").strip().upper()
                is_primary = answer.startswith("SIM")

                if not is_primary:
                    lic["_relevance_source"] = "keyword_peripheral"
                    lic["_confidence_score"] = 30
                    reclassified += 1
                    logger.debug(
                        f"Post-filter LLM: DEMOTED idx={idx} "
                        f"objeto='{objeto[:80]}...' answer='{answer}'"
                    )
            except Exception as e:
                # Fail-open: keep original confidence on LLM error
                logger.warning(
                    f"Post-filter LLM: error for idx={idx}, keeping original: {e}"
                )

    tasks = [_classify_one(idx, lic) for idx, lic in items_to_check]
    await asyncio.gather(*tasks)

    logger.info(
        f"Post-filter LLM: reclassified {reclassified}/{len(items_to_check)} "
        f"items as peripheral for sector '{sector_name}'"
    )

    # Re-sort if any items were reclassified (demoted items sink to bottom)
    if reclassified > 0:
        def _post_filter_sort_key(lic: dict) -> tuple:
            conf = lic.get("_confidence_score", 50)
            combined = lic.get("_combined_score", conf)
            valor = float(lic.get("valorTotalEstimado") or lic.get("valorEstimado") or 0)
            return (-combined, -conf, -valor)

        ctx.licitacoes_filtradas.sort(key=_post_filter_sort_key)
