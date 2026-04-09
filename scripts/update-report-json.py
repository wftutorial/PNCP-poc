#!/usr/bin/env python3
"""Update report JSON with document analysis and reclassifications."""
import json

INPUT = "docs/reports/data-24515063000149-2026-03-17.json"

with open(INPUT, encoding="utf-8") as f:
    d = json.load(f)

# Reclassify ALL editais based on document analysis (Phase 2-3)
reclassifications = {
    0: ("NÃO RECOMENDADO", "Prazo encerrado (0 dias restantes). Concorrência presencial em Seara (488km)."),
    1: ("NÃO RECOMENDADO", "Vetado: licitação presencial a 754km da sede — logística inviável."),
    2: ("NÃO RECOMENDADO", "Vetado: licitação presencial a 754km da sede — logística inviável."),
    3: ("NÃO RECOMENDADO", "Vetado: licitação presencial a 754km da sede — logística inviável."),
    4: ("NÃO RECOMENDADO", "Score de viabilidade insuficiente (20). Pavimentação — CNAE 4120-4 incompatível com pavimentação asfáltica (CNAE 4211-1). Sem atestados técnicos na área."),
    5: ("NÃO RECOMENDADO", "Pavimentação asfáltica (CBUQ) — CNAE 4120-4 (construção de edifícios) incompatível. Exige atestados de pavimentação que a empresa não possui."),
    6: ("NÃO RECOMENDADO", "Pavimentação em CBUQ — CNAE 4120-4 incompatível com obras de pavimentação rodoviária. Exige atestados específicos de pavimentação."),
    7: ("NÃO RECOMENDADO", "Construção de ponte em concreto armado com vigas protendidas — obra altamente especializada. CNAE 4120-4 incompatível. Exige atestados de construção de ponte."),
    8: ("NÃO RECOMENDADO", "Construção de ponte em concreto armado — CNAE 4120-4 incompatível com pontes (CNAE 4211-1). Sem preferência ME/EPP. Exige atestados de ponte inexistentes."),
    9: ("NÃO RECOMENDADO", "Pavimentação asfáltica (CBUQ) — CNAE 4120-4 incompatível com pavimentação."),
    10: ("NÃO RECOMENDADO", "Vetado: licitação presencial a 729km da sede — logística inviável."),
    11: ("NÃO RECOMENDADO", "Vetado: licitação presencial a 646km da sede — logística inviável."),
    12: ("AVALIAR COM CAUTELA",
         "CNAE 4120-4 compatível (construção de casas populares — Programa Casa Catarina). "
         "Capital mínimo R$342 mil atendido (empresa tem R$1,15M). "
         "Principal barreira: exigência de CAT (Certidão de Acervo Técnico) comprovando obra similar. "
         "Participação depende de o responsável técnico possuir acervo pessoal em construção habitacional. "
         "Sessão em 01/04/2026 — prazo viável. Distância de 380km é desafio logístico moderado."),
    13: ("NÃO RECOMENDADO",
         "Pavimentação de 4,7km de estrada rural — CNAE 4120-4 incompatível com pavimentação rodoviária. "
         "Subcontratação expressamente PROIBIDA. Exige atestados de pavimentação rodoviária rural."),
    14: ("NÃO RECOMENDADO", "Vetado: licitação presencial a 581km da sede — logística inviável."),
    15: ("NÃO RECOMENDADO", "Vetado: licitação presencial a 646km da sede — logística inviável."),
    16: ("AVALIAR COM CAUTELA",
         "CNAE 4120-4 compatível (construção de 30 casas populares — Programa Casa Catarina). "
         "Capital mínimo R$372 mil atendido (empresa tem R$1,15M). "
         "Principal barreira: exigência de CAT comprovando obra similar. "
         "Participação depende de o responsável técnico possuir acervo pessoal em construção habitacional. "
         "Prazo de execução 360 dias é razoável. Distância de 181km é viável."),
    17: ("NÃO RECOMENDADO",
         "Objeto é CONSULTORIA ESPECIALIZADA para supervisão e fiscalização de reforma de barragem — "
         "não é execução de obra. CNAE 4120-4 incompatível com serviços de consultoria de engenharia."),
    18: ("NÃO RECOMENDADO", "Vetado: limite do Simples Nacional excedido (edital R$5,31M > R$4,8M)."),
    19: ("NÃO RECOMENDADO", "Vetado: capital social insuficiente e limite do Simples Nacional excedido (edital R$23,1M)."),
    20: ("NÃO RECOMENDADO",
         "Pavimentação asfáltica (CBUQ) — CNAE 4120-4 incompatível com pavimentação. "
         "Exige atestados de pavimentação que a empresa não possui."),
    21: ("NÃO RECOMENDADO", "Vetado: capital social insuficiente e limite do Simples Nacional excedido (edital R$17,9M)."),
    22: ("NÃO RECOMENDADO",
         "Transporte de pedras detonadas e saibro em caminhão caçamba — "
         "objeto completamente fora do escopo de construção civil. CNAE 4120-4 incompatível."),
    23: ("PARTICIPAR",
         "Credenciamento para serviços de mão de obra em construção civil — CNAE 4120-4 compatível. "
         "Habilitação simplíssima: sem CAT, sem capital mínimo, sem índices financeiros. "
         "Valor baixo (R$107 mil), mas pode servir como PRIMEIRO CONTRATO GOVERNAMENTAL "
         "para construir histórico de acervo técnico. Distância de 145km é viável. "
         "Credenciamento aberto até 31/12/2026."),
    24: ("PARTICIPAR",
         "Credenciamento para serviços de mão de obra em construção civil — mesmo município e mesmas condições. "
         "CNAE compatível, habilitação simplíssima. Valor R$96 mil. "
         "Estratégico para construir histórico de contratos governamentais."),
}

for idx, (rec, just) in reclassifications.items():
    if idx < len(d["editais"]):
        d["editais"][idx]["recomendacao"] = rec
        d["editais"][idx]["justificativa"] = just

# Add analise_documental for key editais
d["editais"][23]["analise_documental"] = {
    "ficha_tecnica": "Inexigibilidade 28/2026, Credenciamento Art. 74 IV e Art. 79 I da Lei 14.133/21. Vigência até 31/12/2026. Pagamento 30 dias após NF.",
    "habilitacao": "Simplíssima: ato constitutivo, CNPJ, CND Federal, FGTS, Estadual, Municipal, CNDT, certidão falência. SEM CAT, SEM capital mínimo, SEM índices financeiros.",
    "red_flags": "Valor baixo (R$107K total), demanda incerta, margem mínima (preço fixado pelo órgão).",
    "resumo": "Credenciamento aberto para mão de obra em construção civil. Habilitação mais simples possível. Porta de entrada ideal para primeiro contrato governamental."
}

d["editais"][24]["analise_documental"] = {
    "ficha_tecnica": "Inexigibilidade, Credenciamento similar ao edital anterior. Vigência até 31/12/2026.",
    "habilitacao": "Simplíssima: mesmas condições do edital anterior.",
    "red_flags": "Valor baixo, demanda incerta.",
    "resumo": "Segundo credenciamento do mesmo município. Mesmas condições favoráveis."
}

d["editais"][12]["analise_documental"] = {
    "ficha_tecnica": "Concorrência Eletrônica 06/2026/PMJ, Proc. 52/2026. Sessão 01/04/2026 às 13h30. Empreitada por preço global. Vigência 15 meses.",
    "habilitacao": "CAT obrigatória (obras semelhantes), capital mínimo 10% (R$342K — atendido), índices LG/SG/LC >= 1,0, CND Federal/FGTS/Estadual/Municipal/CNDT, certidão falência, consultas TCU/CNJ. RT deve acompanhar semanalmente.",
    "red_flags": "CAT obrigatória sem contratos anteriores. Pagamento vinculado a recursos estaduais (Casa Catarina) — risco de atraso. RT deve estar na obra semanalmente com comprovação fotográfica.",
    "resumo": "Construção de casas populares (Casa Catarina) em Joaçaba. CNAE 4120-4 perfeitamente compatível. Capital OK. Única barreira: CAT que exige acervo do RT."
}

d["editais"][16]["analise_documental"] = {
    "ficha_tecnica": "Concorrência Eletrônica 01/2026-FMAS. Sessão 07/04/2026 às 09h. Empreitada por preço global. Prazo execução 360 dias. Vigência até 31/12/2027.",
    "habilitacao": "CAT obrigatória, capital mínimo 10% (R$372K — atendido), índices LG/SG/LC >= 1,0, CND Federal/FGTS/Estadual/Municipal/CNDT, certidão falência. Registro CREA/CAU.",
    "red_flags": "CAT obrigatória. Recursos vinculados ao programa estadual Casa Catarina — risco de atraso na liberação. Consórcio não permitido.",
    "resumo": "Construção de 30 unidades habitacionais populares em Urussanga. CNAE compatível. Capital OK. Barreira: CAT de obras similares."
}

# Add delivery_validation
d["delivery_validation"] = {
    "gate_deterministic": "WARNINGS",
    "gate_adversarial": "PENDING",
    "revisions_made": [],
    "reader_persona": "Dono de microempresa de construção civil em São José/SC, sem contratos governamentais, buscando primeira oportunidade B2G"
}

with open(INPUT, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

# Print summary
participar = sum(1 for e in d["editais"] if e.get("recomendacao") == "PARTICIPAR")
avaliar = sum(1 for e in d["editais"] if e.get("recomendacao") == "AVALIAR COM CAUTELA")
nr = sum(1 for e in d["editais"] if e.get("recomendacao") == "NÃO RECOMENDADO")
print(f"JSON atualizado: {participar} PARTICIPAR, {avaliar} AVALIAR COM CAUTELA, {nr} NÃO RECOMENDADO")
