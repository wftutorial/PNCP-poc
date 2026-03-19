#!/usr/bin/env python3
"""
Estimador de custo de proposta para sessões presenciais.

Calcula custo estimado de deslocamento, hospedagem, alimentação,
pedágio e tempo técnico com base na distância sede→edital.

Usage (como módulo):
    from lib.cost_estimator import estimate_proposal_cost
    cost = estimate_proposal_cost(distancia_km=350, duracao_horas=4.5)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CostParams:
    """Parâmetros configuráveis do modelo de custo."""
    custo_km: float = 0.80                  # R$/km (ANTT referência)
    diaria_hospedagem_interior: float = 180.0  # R$ interior
    diaria_hospedagem_capital: float = 280.0   # R$ capital
    per_diem_alimentacao: float = 80.0       # R$/dia
    custo_hora_tecnico: float = 150.0        # R$/hora
    horas_sessao: float = 4.0               # horas estimadas em sessão presencial
    limiar_hospedagem_km: float = 200.0      # acima disso: precisa hospedagem
    limiar_duas_diarias_km: float = 500.0    # acima disso: 2 diárias
    pedagio_por_faixa: dict = field(default_factory=lambda: {
        100: 0.0,       # até 100km: sem pedágio
        300: 30.0,      # 100-300km: ~R$30
        600: 80.0,      # 300-600km: ~R$80
        1000: 150.0,    # 600-1000km: ~R$150
        99999: 250.0,   # >1000km: ~R$250
    })


DEFAULT_PARAMS = CostParams()


def estimate_proposal_cost(
    distancia_km: float | None,
    duracao_horas: float | None,
    is_capital: bool = False,
    is_eletronico: bool = False,
    params: CostParams | None = None,
) -> dict[str, Any]:
    """Estima custo de proposta para participação em edital.

    Args:
        distancia_km: Distância sede→local em km (OSRM)
        duracao_horas: Tempo de viagem em horas (OSRM, uma via)
        is_capital: Se o destino é capital de estado
        is_eletronico: Se a modalidade é eletrônica (sem deslocamento)
        params: Parâmetros customizáveis (default: DEFAULT_PARAMS)

    Returns:
        dict com total, breakdown, e metadata
    """
    p = params or DEFAULT_PARAMS

    # Sessão eletrônica: custo mínimo (só tempo técnico de preparo)
    if is_eletronico:
        tempo_preparo = p.horas_sessao * p.custo_hora_tecnico
        return {
            "total": round(tempo_preparo, 2),
            "modalidade_tipo": "eletronica",
            "breakdown": {
                "deslocamento": 0.0,
                "hospedagem": 0.0,
                "alimentacao": 0.0,
                "pedagio": 0.0,
                "tempo_tecnico": round(tempo_preparo, 2),
            },
            "premissas": {
                "horas_preparo": p.horas_sessao,
                "custo_hora": p.custo_hora_tecnico,
            },
            "nota": "Sessão eletrônica — custo limitado a tempo de preparação da proposta",
        }

    # Se não tem dados de distância, retornar indisponível
    if distancia_km is None or distancia_km <= 0:
        return {
            "total": None,
            "modalidade_tipo": "presencial",
            "breakdown": None,
            "premissas": None,
            "nota": "Distância indisponível — custo não calculado",
        }

    dur = duracao_horas or (distancia_km / 60.0)  # fallback: ~60km/h

    # 1. Deslocamento (ida + volta)
    deslocamento = distancia_km * 2 * p.custo_km

    # 2. Hospedagem
    hospedagem = 0.0
    diarias = 0
    if distancia_km > p.limiar_hospedagem_km:
        diaria = p.diaria_hospedagem_capital if is_capital else p.diaria_hospedagem_interior
        diarias = 2 if distancia_km > p.limiar_duas_diarias_km else 1
        hospedagem = diarias * diaria

    # 3. Alimentação
    # Se precisa hospedagem: dias completos; senão: 1 refeição
    if diarias > 0:
        alimentacao = (diarias + 1) * p.per_diem_alimentacao  # +1 dia de viagem
    elif distancia_km > 50:
        alimentacao = p.per_diem_alimentacao  # 1 refeição
    else:
        alimentacao = 0.0

    # 4. Pedágio (por faixa)
    pedagio = 0.0
    for faixa_km, valor in sorted(p.pedagio_por_faixa.items()):
        if distancia_km <= faixa_km:
            pedagio = valor * 2  # ida + volta
            break

    # 5. Tempo técnico (viagem + sessão)
    horas_viagem = dur * 2  # ida + volta
    horas_total = horas_viagem + p.horas_sessao
    tempo_tecnico = horas_total * p.custo_hora_tecnico

    total = deslocamento + hospedagem + alimentacao + pedagio + tempo_tecnico

    return {
        "total": round(total, 2),
        "modalidade_tipo": "presencial",
        "breakdown": {
            "deslocamento": round(deslocamento, 2),
            "hospedagem": round(hospedagem, 2),
            "alimentacao": round(alimentacao, 2),
            "pedagio": round(pedagio, 2),
            "tempo_tecnico": round(tempo_tecnico, 2),
        },
        "premissas": {
            "distancia_km": round(distancia_km, 1),
            "duracao_horas_via": round(dur, 1),
            "horas_viagem_total": round(horas_viagem, 1),
            "horas_sessao": p.horas_sessao,
            "diarias_hospedagem": diarias,
            "custo_km": p.custo_km,
            "custo_hora_tecnico": p.custo_hora_tecnico,
        },
        "nota": _build_nota(distancia_km, diarias, is_capital),
    }


def _build_nota(distancia_km: float, diarias: int, is_capital: bool) -> str:
    """Gera nota explicativa do custo."""
    parts = []
    if distancia_km <= 50:
        parts.append("Proximidade favorável — deslocamento local")
    elif distancia_km <= 200:
        parts.append("Deslocamento regional — sem necessidade de hospedagem")
    elif distancia_km <= 500:
        parts.append(f"Deslocamento interestadual — {diarias} diária(s) de hospedagem")
    else:
        parts.append(f"Deslocamento de longa distância — {diarias} diárias de hospedagem")

    if is_capital:
        parts.append("destino em capital (custo de hospedagem majorado)")

    return "; ".join(parts)


def estimate_roi_simple(
    valor_edital: float | None,
    custo_proposta: float | None,
) -> dict[str, Any] | None:
    """Calcula ROI simplificado da participação.

    Returns:
        dict com ratio, classificação, ou None se dados insuficientes
    """
    if not valor_edital or not custo_proposta or custo_proposta <= 0:
        return None

    ratio = valor_edital / custo_proposta

    if ratio >= 500:
        classificacao = "EXCELENTE"
    elif ratio >= 100:
        classificacao = "BOM"
    elif ratio >= 30:
        classificacao = "MODERADO"
    elif ratio >= 10:
        classificacao = "MARGINAL"
    else:
        classificacao = "DESFAVORAVEL"

    return {
        "ratio_valor_custo": round(ratio, 0),
        "classificacao": classificacao,
        "custo_percentual_valor": round((custo_proposta / valor_edital) * 100, 2),
    }
