"""Generate Markdown version of LCM proposta."""
import json
from datetime import datetime, timedelta

with open("docs/propostas/data-01721078000168-2026-03-12.json", encoding="utf-8") as f:
    data = json.load(f)

emp = data["empresa"]
editais = data["editais"]
resumo = data["resumo_executivo"]
intel = data["inteligencia_mercado"]
proximos = data["proximos_passos"]

today = datetime.now()
validity = today + timedelta(days=15)

n_part = sum(1 for e in editais if e["recomendacao"] == "PARTICIPAR")
n_aval = sum(1 for e in editais if e["recomendacao"] == "AVALIAR COM CAUTELA")
total_val = sum(e["valor_estimado"] for e in editais)
total_part_val = sum(e["valor_estimado"] for e in editais if e["recomendacao"] == "PARTICIPAR")


def fmt_val(v):
    if v >= 1e6:
        return f"R$ {v/1e6:.1f}M"
    elif v >= 1e3:
        return f"R$ {v/1e3:.0f}K"
    else:
        return f"R$ {v:,.2f}"


def fmt_date(d):
    if not d or "-" not in d:
        return d or "N/D"
    parts = d.split("-")
    return f"{parts[2]}/{parts[1]}/{parts[0]}"


md = []
md.append("# Proposta de Consultoria em Licitacoes Publicas")
md.append(f"## Preparada exclusivamente para **{emp['nome_fantasia']}**\n")
md.append("| | |")
md.append("|---|---|")
md.append(f"| **Data** | {today.strftime('%d/%m/%Y')} |")
md.append(f"| **Validade** | 15 dias (ate {validity.strftime('%d/%m/%Y')}) |")
md.append(f"| **CNPJ** | {emp['cnpj']} |")
md.append("| **Consultor** | Tiago Sasaki |")
md.append("| **Contato** | (48) 9 8834-4559 |")
md.append("")

# 1. Carta ao Decisor
decisor = emp["qsa"][0]["nome"] if emp.get("qsa") else "Prezado(a) Diretor(a)"
md.append("---\n## 1. Carta ao Decisor\n")
md.append(f"Sr. {decisor},\n")
md.append(
    f"Como engenheiro da Secretaria de Estado da Infraestrutura de SC, acompanho diariamente "
    f"o volume de obras publicas licitadas no estado. Na minha atividade paralela de consultoria, "
    f"faco o caminho inverso: identifico, para empresas como a {emp['nome_fantasia']}, quais dessas "
    f"oportunidades tem aderencia real ao perfil tecnico e financeiro da empresa.\n"
)
md.append(
    f"Nos ultimos 30 dias, mapeei **{len(editais)} editais abertos em SC** diretamente compativeis "
    f"com os CNAEs da {emp['nome_fantasia']}, totalizando **{fmt_val(total_val)} em valor estimado**.\n"
)
md.append("Os dados sao publicos. **A analise e o diferencial.**\n")

# 2. Diagnostico
md.append("---\n## 2. Diagnostico da Empresa\n")
md.append("| Campo | Valor |")
md.append("|---|---|")
md.append(f"| **Razao Social** | {emp['razao_social']} |")
md.append(f"| **CNPJ** | {emp['cnpj']} |")
md.append(f"| **CNAE Principal** | {emp['cnae_principal']} |")
md.append(f"| **CNAEs Secundarios** | {emp['cnaes_secundarios']} |")
md.append(f"| **Porte** | {emp['porte']} |")
md.append(f"| **Capital Social** | R$ {emp['capital_social']:,.2f} |")
md.append(f"| **Sede** | {emp['cidade_sede']}/{emp['uf_sede']} |")
md.append(f"| **Socio-Administrador** | {decisor} |")
md.append(f"| **Situacao Cadastral** | {emp['situacao_cadastral']} |")
md.append("| **Sancoes Gov.** | NENHUMA (CEIS, CNEP, CEPIM, CEAF) |")
md.append("")

md.append("### Pontos Fortes\n")
md.append("- 29 anos de mercado (fundada em 1997) -- longevidade da peso na habilitacao")
md.append("- CNAE principal (4120-4) posiciona no nucleo do setor de construcao")
md.append("- 9 CNAEs secundarios ampliam elegibilidade (terra, instalacoes, hidraulica)")
md.append("- Capital social de R$ 1,6M qualifica para editais ate R$ 8M")
md.append("- Zero sancoes -- apta a licitar em qualquer esfera")
md.append("- Sede em Itajai -- posicao estrategica no litoral catarinense")
md.append("")

# 3. Radiografia do Mercado
md.append("---\n## 3. Radiografia do Mercado -- SC Engenharia\n")
md.append(f"{intel['panorama']}\n")
md.append("### Numeros-chave\n")
md.append("| Metrica | Valor |")
md.append("|---|---|")
md.append(f"| **Editais mapeados (30 dias)** | {len(editais)} |")
md.append(f"| **Valor total em disputa** | {fmt_val(total_val)} |")
md.append(f"| **Editais PARTICIPAR** | {n_part} ({fmt_val(total_part_val)}) |")
md.append(f"| **Editais AVALIAR** | {n_aval} |")
md.append("| **Oportunidades PR (30d)** | 83 editais (R$ 412,6M) |")
md.append("| **Oportunidades RS (30d)** | 47 editais (R$ 80,3M) |")
md.append("")

md.append("### Tendencias\n")
for t in intel.get("tendencias", []):
    md.append(f"- {t}")
md.append("")

# 4. Top Oportunidades
md.append("---\n## 4. Top Oportunidades\n")
md.append("| # | Rec. | Valor | Municipio | Encerramento | Objeto |")
md.append("|---|---|---|---|---|---|")
for i, e in enumerate(editais[:30]):
    val_f = fmt_val(e["valor_estimado"])
    enc = fmt_date(e["data_encerramento"])
    obj = e["objeto"][:70].replace("|", "/")
    rec = "PARTICIPAR" if e["recomendacao"] == "PARTICIPAR" else "AVALIAR"
    md.append(f"| {i+1} | {rec} | {val_f} | {e['municipio']} | {enc} | {obj} |")
md.append("")

if len(editais) > 30:
    md.append(f"*...e mais {len(editais)-30} editais. Lista completa no JSON de dados.*\n")

# 5. Analise Detalhada
participar = [e for e in editais if e["recomendacao"] == "PARTICIPAR"]
if participar:
    me = participar[0]
    md.append("---\n## 5. Analise Detalhada -- Edital Prioritario\n")
    md.append(f"**{me['objeto']}**\n")
    md.append("| Campo | Detalhe |")
    md.append("|---|---|")
    md.append(f"| **Orgao** | {me['orgao']} |")
    md.append(f"| **Municipio** | {me['municipio']}/{me['uf']} |")
    md.append(f"| **Valor Estimado** | R$ {me['valor_estimado']:,.2f} |")
    md.append(f"| **Modalidade** | {me['modalidade']} |")
    md.append(f"| **Encerramento** | {fmt_date(me['data_encerramento'])} ({me['dias_restantes']} dias) |")
    md.append(f"| **Fonte** | {me['fonte']} |")
    md.append("")
    an = me.get("analise", {})
    md.append("### Analise\n")
    for k, v in an.items():
        md.append(f"- **{k.title()}:** {v}")
    md.append("")

# 6. ROI
md.append("---\n## 6. Dimensionamento da Oportunidade\n")
md.append("### Cenario COM vs SEM monitoramento\n")
md.append("| Metrica | SEM monitoramento | COM monitoramento |")
md.append("|---|---|---|")
md.append("| Editais identificados/mes | 3-5 (busca manual) | 15-25 (varredura automatica) |")
md.append("| Tempo de preparo | Reativo (descobre tarde) | Proativo (alerta no dia 1) |")
md.append("| Propostas enviadas/mes | 1-2 | 5-8 |")
md.append("| Taxa de vitoria estimada | 10-15% | 20-30% (propostas melhor preparadas) |")
md.append(
    f"| Receita gov incremental/ano | - | {fmt_val(total_part_val*0.2)} a {fmt_val(total_part_val*0.3)} |"
)
md.append("")

custo_anual = 2500 * 12
receita_low = total_part_val * 0.15
roi_low = (receita_low - custo_anual) / custo_anual * 100
md.append("### ROI Estimado (Pacote Semanal)\n")
md.append(f"- **Investimento anual:** R$ {custo_anual:,.0f}")
md.append(f"- **Receita incremental estimada:** {fmt_val(receita_low)} a {fmt_val(total_part_val*0.25)}")
md.append(f"- **ROI conservador:** {roi_low:,.0f}%")
md.append("- **Payback:** < 1 mes (um contrato ganho paga anos de consultoria)")
md.append("")

# 7. Pacotes
md.append("---\n## 7. Pacotes de Monitoramento\n")
md.append("| | Mensal | **Semanal (Rec.)** | Diario |")
md.append("|---|---|---|---|")
md.append("| **Preco** | R$ 997/mes | **R$ 2.500/mes** | R$ 4.997/mes |")
md.append("| **Relatorios** | 1x/mes | 4x semana + 1x/mes | Diario + semanal + mensal |")
md.append("| **Analise PDF** | Ate 3 editais | Ate 8 editais | Ilimitada |")
md.append("| **UFs** | SC | SC+PR+RS | 5 estados |")
md.append("| **Suporte** | Comercial | Estendido | Dedicado |")
md.append("| **Anual** | Pague 10, leve 12 | Pague 10, leve 12 | Pague 10, leve 12 |")
md.append("")

# 8. Quem Analisa
md.append("---\n## 8. Quem Analisa Seus Editais\n")
md.append(
    "**Tiago Sasaki** -- Engenheiro Civil, servidor efetivo da Secretaria de Estado "
    "da Infraestrutura de SC ha 7 anos.\n"
)
md.append("- 500+ propostas de habilitacao analisadas **pelo lado do orgao**")
md.append("- Conhece os criterios nao escritos das comissoes de licitacao")
md.append("- Sabe onde 80% das inabilitacoes acontecem (e como evita-las)")
md.append("- Historico de pagamento dos orgaos -- sabe quem paga em dia e quem atrasa")
md.append("- SmartLic: tecnologia proprietaria de varredura e classificacao de editais")
md.append("")

# 9. Condicoes
md.append("---\n## 9. Condicoes Comerciais\n")
md.append("**Pacote recomendado: Semanal -- R$ 2.500/mes**\n")
md.append("- Forma de pagamento: Boleto, PIX ou Cartao")
md.append("- Contrato minimo: 3 meses")
md.append("- Cancelamento: 30 dias de antecedencia")
md.append(
    f"- **Condicao especial:** Primeiro mes de cortesia para contratacoes ate "
    f"{validity.strftime('%d/%m/%Y')}"
)
md.append("")

# 10. Proximos Passos
md.append("---\n## 10. Proximos Passos\n")
for p in proximos:
    md.append(f"- [{p['prioridade']}] **{p['acao']}** -- {p['prazo']}")
md.append("")

# CTA
soonest = sorted(
    [e for e in editais if e["dias_restantes"] > 0],
    key=lambda e: e["dias_restantes"],
)
if soonest:
    md.append(f"---\n### O proximo edital encerra em {soonest[0]['dias_restantes']} dias.\n")
    md.append("**Para iniciar, responda este WhatsApp ou ligue para (48) 9 8834-4559**\n")

md.append("\n---\n*Tiago Sasaki -- Consultor de Licitacoes (48) 9 8834-4559*")

output = "docs/propostas/proposta-01721078000168-lcm-construcoes-2026-03-12.md"
with open(output, "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print(f"Markdown gerado: {output}")
