"""
Gerador de PDF de Proposta Comercial B2G
Usa reportlab para gerar PDF profissional a partir do JSON de dados.
v4 — Setor-agnóstico, entregas alinhadas com /intel-busca, sem oportunidades
     individuais, capital 10x, nome fallback, accent map expandido.
"""
import argparse
import datetime
import json
import re
import sys
from collections import Counter
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)

# --- Dimensions ---
PAGE_W, PAGE_H = A4
MARGIN = 20 * mm
CONTENT_W = PAGE_W - 2 * MARGIN  # ~170mm

# --- Colors ---
NAVY = HexColor("#1a365d")
DARK_BLUE = HexColor("#2c5282")
MEDIUM_BLUE = HexColor("#3182ce")
LIGHT_BLUE = HexColor("#ebf8ff")
LIGHT_GRAY = HexColor("#f7fafc")
MEDIUM_GRAY = HexColor("#e2e8f0")
DARK_GRAY = HexColor("#2d3748")
WHITE = white

FOOTER_TEXT = "Tiago Sasaki — Consultor de Licitações (48) 9 8834-4559"

# ---------------------------------------------------------------------------
# Accent fixer — JSON data arrives WITHOUT accents (pure ASCII PT-BR)
# ---------------------------------------------------------------------------
_ACCENT_MAP = [
    # -ção / -ções endings (most common)
    (r"\bExecucao\b", "Execução"), (r"\bexecucao\b", "execução"),
    (r"\bmovimentacao\b", "movimentação"), (r"\bMovimentacao\b", "Movimentação"),
    (r"\bConstrucao\b", "Construção"), (r"\bconstrucao\b", "construção"),
    (r"\bPavimentacao\b", "Pavimentação"), (r"\bpavimentacao\b", "pavimentação"),
    (r"\blicitacao\b", "licitação"), (r"\bLicitacao\b", "Licitação"),
    (r"\blicitacoes\b", "licitações"), (r"\bLicitacoes\b", "Licitações"),
    (r"\bcompeticao\b", "competição"), (r"\bCompeticao\b", "Competição"),
    (r"\bhabitacao\b", "habitação"), (r"\bHabitacao\b", "Habitação"),
    (r"\bedificacao\b", "edificação"), (r"\bEdificacao\b", "Edificação"),
    (r"\brestricao\b", "restrição"), (r"\bRestricao\b", "Restrição"),
    (r"\bdeclaracao\b", "declaração"), (r"\bDeclaracao\b", "Declaração"),
    (r"\binstalacoes\b", "instalações"), (r"\bInstalacoes\b", "Instalações"),
    (r"\bcontratacao\b", "contratação"), (r"\bContratacao\b", "Contratação"),
    (r"\bcontratacoes\b", "contratações"), (r"\bContratacoes\b", "Contratações"),
    (r"\bConcorrencia\b", "Concorrência"), (r"\bconcorrencia\b", "concorrência"),
    (r"\bcomplementacao\b", "complementação"), (r"\bComplementacao\b", "Complementação"),
    (r"\bprecificacao\b", "precificação"), (r"\bPrecificacao\b", "Precificação"),
    (r"\bdiversificacao\b", "diversificação"),
    (r"\bparticipacao\b", "participação"), (r"\bParticipacao\b", "Participação"),
    (r"\biluminacao\b", "iluminação"),
    (r"\bimpugnacao\b", "impugnação"),
    (r"\bpreparacao\b", "preparação"),
    (r"\bmobilizacao\b", "mobilização"),
    (r"\bescavacao\b", "escavação"),
    (r"\binformacao\b", "informação"), (r"\binformacoes\b", "informações"),
    (r"\bsituacao\b", "situação"),
    (r"\bavaliacao\b", "avaliação"),
    (r"\bclassificacao\b", "classificação"),
    (r"\bobservacao\b", "observação"),
    (r"\bprojecao\b", "projeção"), (r"\bprojecoes\b", "projeções"),
    (r"\brecomendacao\b", "recomendação"),
    # -ão endings
    (r"\bpavilhao\b", "pavilhão"), (r"\bPavilhao\b", "Pavilhão"),
    (r"\borgao\b", "órgão"), (r"\bOrgao\b", "Órgão"),
    (r"\bPregao\b", "Pregão"), (r"\bpregao\b", "pregão"),
    (r"\bsessao\b", "sessão"), (r"\bSessao\b", "Sessão"),
    (r"\bpadrao\b", "padrão"), (r"\bPadrao\b", "Padrão"),
    (r"\bsao\b", "são"), (r"\bSao\b", "São"),
    (r"\bnao\b", "não"), (r"\bNao\b", "Não"),
    (r"\bentao\b", "então"),
    # -ência / -ância
    (r"\binteligencia\b", "inteligência"), (r"\bInteligencia\b", "Inteligência"),
    (r"\bfrequencia\b", "frequência"), (r"\bFrequencia\b", "Frequência"),
    (r"\breferencia\b", "referência"), (r"\bReferencia\b", "Referência"),
    (r"\bexperiencia\b", "experiência"), (r"\bExperiencia\b", "Experiência"),
    (r"\bexigencias\b", "exigências"), (r"\bExigencias\b", "Exigências"),
    (r"\bconcorrentes\b", "concorrentes"),  # correct already
    (r"\bCertidao\b", "Certidão"), (r"\bcertidao\b", "certidão"),
    (r"\bciencia\b", "ciência"),
    (r"\bvirgencia\b", "vigência"),
    (r"\bantecedencia\b", "antecedência"),
    (r"\bsuficiencia\b", "suficiência"),
    # -ível / -ável
    (r"\bcompativel\b", "compatível"), (r"\bCompativel\b", "Compatível"),
    (r"\bpossivel\b", "possível"), (r"\bPossivel\b", "Possível"),
    (r"\bdisponivel\b", "disponível"), (r"\bDisponivel\b", "Disponível"),
    (r"\bprovavel\b", "provável"), (r"\bProvavel\b", "Provável"),
    (r"\bfactivel\b", "factível"),
    (r"\bacessivel\b", "acessível"),
    # -ico / -ica / -icos
    (r"\bgenericos\b", "genéricos"), (r"\bGenerico\b", "Genérico"),
    (r"\blogistico\b", "logístico"), (r"\bLogistico\b", "Logístico"),
    (r"\bespecifico\b", "específico"), (r"\bEspecifico\b", "Específico"),
    (r"\bespecifica\b", "específica"), (r"\bespecificos\b", "específicos"),
    (r"\basfaltica\b", "asfáltica"), (r"\bAsfaltica\b", "Asfáltica"),
    (r"\bhidraulicas\b", "hidráulicas"), (r"\bHidraulicas\b", "Hidráulicas"),
    (r"\beletrica\b", "elétrica"), (r"\bEletrica\b", "Elétrica"),
    (r"\beletricas\b", "elétricas"),
    (r"\btecnica\b", "técnica"), (r"\bTecnica\b", "Técnica"),
    (r"\btecnico\b", "técnico"), (r"\bTecnico\b", "Técnico"),
    (r"\bjuridica\b", "jurídica"), (r"\bJuridica\b", "Jurídica"),
    (r"\beletronico\b", "eletrônico"), (r"\bEletronico\b", "Eletrônico"),
    (r"\beletronica\b", "eletrônica"), (r"\bEletronica\b", "Eletrônica"),
    # -ário / -ária
    (r"\borcamentaria\b", "orçamentária"), (r"\bOrcamentaria\b", "Orçamentária"),
    (r"\bsecundarios\b", "secundários"),
    (r"\bnecessario\b", "necessário"),
    (r"\bhabitacionais\b", "habitacionais"),  # correct
    # Place names
    (r"\bDionisio\b", "Dionísio"),
    (r"\bJoacaba\b", "Joaçaba"),
    (r"\bChapeco\b", "Chapecó"),
    (r"\bBalneario\b", "Balneário"),
    # -ço / -ça
    (r"\bpreco\b", "preço"), (r"\bPreco\b", "Preço"),
    (r"\bprecos\b", "preços"),
    (r"\bservico\b", "serviço"), (r"\bservicos\b", "serviços"),
    (r"\bGoncalves\b", "Gonçalves"),
    # Misc
    (r"\bMunicipio\b", "Município"), (r"\bmunicipio\b", "município"),
    (r"\bmunicipios\b", "municípios"), (r"\bMunicipios\b", "Municípios"),
    # REMOVED: (r"\be\b(...)", "é") — too aggressive, converts "e" conjunction to "é" verb
    # e.g. "terra e drenagem" → "terra é drenagem" (WRONG). PT-BR "e" conjunction is far more common.
    (r"\buteis\b", "úteis"),
    (r"\bunico\b", "único"),
    (r"\bminimo\b", "mínimo"),
    (r"\bmaximo\b", "máximo"),
    (r"\bultimos\b", "últimos"),
    (r"\bultimo\b", "último"),
    (r"\bindice\b", "índice"), (r"\bindices\b", "índices"),
    (r"\bsolido\b", "sólido"),
    (r"\brobusto\b", "robusto"),  # correct
    (r"\bhistorico\b", "histórico"),
    (r"\bcontabil\b", "contábil"), (r"\bcontabeis\b", "contábeis"),
    (r"\bdotacao\b", "dotação"),
    (r"\bregiao\b", "região"),
    (r"\bnicho\b", "nicho"),  # correct
    (r"\bPropostas\b", "Propostas"),  # correct
    (r"\bhabilitacao\b", "habilitação"), (r"\bHabilitacao\b", "Habilitação"),
    (r"\binabilitacao\b", "inabilitação"), (r"\binabilitacoes\b", "inabilitações"),
    (r"\bsancoes\b", "sanções"), (r"\bSancoes\b", "Sanções"),
    (r"\bsancao\b", "sanção"),
    (r"\bCracas\b", "Praças"),  # unlikely but safe
    (r"\bPraca\b", "Praça"), (r"\bpraca\b", "praça"),
    # --- Procurement/licitação terms (v4 expansion) ---
    (r"\baquisicao\b", "aquisição"), (r"\bAquisicao\b", "Aquisição"),
    (r"\baquisicoes\b", "aquisições"), (r"\bAquisicoes\b", "Aquisições"),
    (r"\bfiscalizacao\b", "fiscalização"), (r"\bFiscalizacao\b", "Fiscalização"),
    (r"\bmedicao\b", "medição"), (r"\bMedicao\b", "Medição"),
    (r"\borcamento\b", "orçamento"), (r"\bOrcamento\b", "Orçamento"),
    (r"\bretencao\b", "retenção"), (r"\bRetencao\b", "Retenção"),
    (r"\bprotocolizacao\b", "protocolização"),
    (r"\binspecao\b", "inspeção"), (r"\bInspecao\b", "Inspeção"),
    (r"\brescisao\b", "rescisão"), (r"\bRescisao\b", "Rescisão"),
    (r"\bprovisao\b", "provisão"),
    (r"\bprestacao\b", "prestação"), (r"\bPrestacao\b", "Prestação"),
    (r"\bcotacao\b", "cotação"), (r"\bcotacoes\b", "cotações"),
    (r"\bautorizacao\b", "autorização"), (r"\bAutorizacao\b", "Autorização"),
    (r"\bhomologacao\b", "homologação"), (r"\bHomologacao\b", "Homologação"),
    (r"\badjudicacao\b", "adjudicação"), (r"\bAdjudicacao\b", "Adjudicação"),
    (r"\bdesclassificacao\b", "desclassificação"),
    (r"\bconcessao\b", "concessão"), (r"\bConcessao\b", "Concessão"),
    (r"\bpermissao\b", "permissão"),
    (r"\bproducao\b", "produção"), (r"\bProducao\b", "Produção"),
    (r"\bmanutencao\b", "manutenção"), (r"\bManutencao\b", "Manutenção"),
    (r"\boperacao\b", "operação"), (r"\bOperacao\b", "Operação"),
    (r"\bimplantacao\b", "implantação"), (r"\bImplantacao\b", "Implantação"),
    (r"\brecuperacao\b", "recuperação"), (r"\bRecuperacao\b", "Recuperação"),
    (r"\bdemolicao\b", "demolição"), (r"\bDemolicao\b", "Demolição"),
    (r"\bsinalizacao\b", "sinalização"), (r"\bSinalizacao\b", "Sinalização"),
    (r"\bdesapropriacao\b", "desapropriação"),
    (r"\bregularizacao\b", "regularização"),
    (r"\bprorrogacao\b", "prorrogação"),
    (r"\badequacao\b", "adequação"), (r"\bAdequacao\b", "Adequação"),
    (r"\bcertificacao\b", "certificação"),
    (r"\bqualificacao\b", "qualificação"), (r"\bQualificacao\b", "Qualificação"),
    # --- Sector-agnostic terms ---
    (r"\btecnologia\b", "tecnologia"),  # correct
    (r"\bsaude\b", "saúde"), (r"\bSaude\b", "Saúde"),
    (r"\beducacao\b", "educação"), (r"\bEducacao\b", "Educação"),
    (r"\balimentacao\b", "alimentação"), (r"\bAlimentacao\b", "Alimentação"),
    (r"\btransporte\b", "transporte"),  # correct
    (r"\bseguranca\b", "segurança"), (r"\bSeguranca\b", "Segurança"),
    (r"\blimpeza\b", "limpeza"),  # correct
    (r"\bcomunicacao\b", "comunicação"), (r"\bComunicacao\b", "Comunicação"),
    (r"\bcapacitacao\b", "capacitação"),
    (r"\bgestao\b", "gestão"), (r"\bGestao\b", "Gestão"),
]

# Pre-compile for performance
_ACCENT_PATTERNS = [(re.compile(pat), repl) for pat, repl in _ACCENT_MAP]


def fix_accents(text):
    """Fix common missing PT-BR accents in text from JSON data."""
    if not text or not isinstance(text, str):
        return text or ""
    for pat, repl in _ACCENT_PATTERNS:
        text = pat.sub(repl, text)
    # Replace any remaining en-dashes with em-dashes
    text = text.replace("\u2013", "\u2014")
    return text


def fmt_date(iso_str):
    """Convert YYYY-MM-DD to DD/MM/YYYY."""
    if not iso_str:
        return ""
    try:
        parts = iso_str.split("-")
        return f"{parts[2]}/{parts[1]}/{parts[0]}"
    except (IndexError, AttributeError):
        return str(iso_str)


def fmt_value(v):
    """Format a numeric value as R$ with Brazilian formatting."""
    if v is None:
        return "R$ 0"
    v = float(v)
    if v >= 1_000_000:
        return f"R$ {v/1_000_000:,.1f}M".replace(",", "X").replace(".", ",").replace("X", ".")
    elif v >= 1_000:
        return f"R$ {v/1_000:,.0f}K".replace(",", ".")
    else:
        return f"R$ {v:,.0f}".replace(",", ".")


def fmt_value_full(v):
    """Format a numeric value as R$ with full precision."""
    if v is None:
        return "R$ 0,00"
    v = float(v)
    return "R$ {:,.2f}".format(v).replace(",", "X").replace(".", ",").replace("X", ".")


def detect_gender(name):
    """Heuristic gender detection for PT-BR first names. Returns 'Sr.' or 'Sra.'."""
    if not name:
        return "Sr."
    first = name.strip().split()[0].lower()
    female_endings = ("a", "e", "ane", "ene", "ine", "ice", "ilde", "ude")
    female_names = {
        "angela", "ana", "maria", "mariana", "juliana", "fernanda", "amanda",
        "patricia", "luciana", "adriana", "cristiane", "rosane", "eliane",
        "simone", "viviane", "diane", "aline", "caroline", "michele",
        "vanessa", "larissa", "beatriz", "roberta", "denise", "raquel",
        "claudia", "silvia", "sandra", "carla", "paula", "lucia",
        "tereza", "teresa", "marta", "rita", "sonia", "rosa",
        "irene", "alice", "helene", "elise", "renata", "camila",
        "leticia", "gabriela", "daniela", "rafaela", "isabela", "priscila",
        "tatiana", "fabiana", "luana", "bruna", "natalia",
    }
    male_names = {
        "andre", "alexandre", "felipe", "henrique", "jose", "dante",
        "jorge", "duarte", "vicente", "bruce", "jaime", "rique",
    }
    if first in male_names:
        return "Sr."
    if first in female_names:
        return "Sra."
    if first.endswith("a") or first.endswith("e"):
        return "Sra."
    return "Sr."


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

def create_styles():
    styles = getSampleStyleSheet()
    add = styles.add

    add(ParagraphStyle(
        'CoverTitle', parent=styles['Title'],
        fontSize=26, leading=32, textColor=NAVY,
        spaceAfter=5 * mm, alignment=TA_CENTER, fontName='Helvetica-Bold',
    ))
    add(ParagraphStyle(
        'CoverSub', parent=styles['Normal'],
        fontSize=14, leading=18, textColor=DARK_BLUE,
        spaceAfter=4 * mm, alignment=TA_CENTER, fontName='Helvetica',
    ))
    add(ParagraphStyle(
        'H1', parent=styles['Heading1'],
        fontSize=15, leading=19, textColor=NAVY,
        spaceBefore=6 * mm, spaceAfter=3 * mm, fontName='Helvetica-Bold',
    ))
    add(ParagraphStyle(
        'H2', parent=styles['Heading2'],
        fontSize=12, leading=15, textColor=DARK_BLUE,
        spaceBefore=4 * mm, spaceAfter=2 * mm, fontName='Helvetica-Bold',
    ))
    add(ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontSize=9.5, leading=13, textColor=DARK_GRAY,
        spaceAfter=2 * mm, fontName='Helvetica', alignment=TA_JUSTIFY,
    ))
    add(ParagraphStyle(
        'BodyBold', parent=styles['Normal'],
        fontSize=9.5, leading=13, textColor=DARK_GRAY,
        spaceAfter=2 * mm, fontName='Helvetica-Bold',
    ))
    add(ParagraphStyle(
        'Quote', parent=styles['Normal'],
        fontSize=9.5, leading=13, textColor=DARK_BLUE,
        spaceAfter=3 * mm, fontName='Helvetica-Oblique',
        leftIndent=8 * mm, rightIndent=8 * mm,
        borderWidth=1, borderColor=MEDIUM_BLUE,
        borderPadding=(5, 8, 5, 8), backColor=LIGHT_BLUE,
    ))
    add(ParagraphStyle(
        'Small', parent=styles['Normal'],
        fontSize=7.5, leading=10, textColor=HexColor("#718096"), fontName='Helvetica',
    ))
    # Cell styles for tables
    add(ParagraphStyle(
        'CellH', parent=styles['Normal'],
        fontSize=8.5, leading=11, textColor=WHITE,
        fontName='Helvetica-Bold', alignment=TA_CENTER,
    ))
    add(ParagraphStyle(
        'Cell', parent=styles['Normal'],
        fontSize=8.5, leading=11, textColor=DARK_GRAY, fontName='Helvetica',
    ))
    add(ParagraphStyle(
        'CellB', parent=styles['Normal'],
        fontSize=8.5, leading=11, textColor=DARK_GRAY, fontName='Helvetica-Bold',
    ))
    add(ParagraphStyle(
        'CellC', parent=styles['Normal'],
        fontSize=8.5, leading=11, textColor=DARK_GRAY,
        fontName='Helvetica', alignment=TA_CENTER,
    ))
    add(ParagraphStyle(
        'CTAWhite', parent=styles['Normal'],
        fontSize=11, leading=15, textColor=WHITE,
        fontName='Helvetica-Bold', alignment=TA_CENTER,
    ))
    add(ParagraphStyle(
        'CTAWhiteSub', parent=styles['Normal'],
        fontSize=9.5, leading=13, textColor=WHITE,
        fontName='Helvetica', alignment=TA_CENTER,
    ))
    add(ParagraphStyle(
        'BadgeWhite', parent=styles['Normal'],
        fontSize=9, leading=12, textColor=WHITE,
        fontName='Helvetica-Bold', alignment=TA_CENTER,
    ))
    return styles


S = None  # global ref set in build_pdf


def P(text, style='Cell'):
    """Wrap text in a Paragraph for proper word-wrap inside table cells."""
    return Paragraph(str(fix_accents(str(text))), S[style])


def make_table(headers, rows, col_widths, header_color=NAVY):
    """Table with Paragraph-wrapped cells for proper word-wrap."""
    hdr = [P(h, 'CellH') for h in headers]
    body = []
    for row in rows:
        body.append([P(c) if not isinstance(c, Paragraph) else c for c in row])
    data = [hdr] + body
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, MEDIUM_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


def make_kv(rows, kw=50 * mm):
    """Key-value 2-column table."""
    vw = CONTENT_W - kw
    data = [[P(k, 'CellB'), P(v)] for k, v in rows]
    t = Table(data, colWidths=[kw, vw])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, MEDIUM_GRAY),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [WHITE, LIGHT_GRAY]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


def hr():
    return HRFlowable(width="100%", thickness=0.8, color=MEDIUM_GRAY, spaceAfter=2 * mm, spaceBefore=2 * mm)


def bullet(text, style='Body'):
    return Paragraph("\u2022  " + fix_accents(text), S[style])


# ---------------------------------------------------------------------------
# PDF Builder
# ---------------------------------------------------------------------------

def build_pdf(data, output_path, pacote_recomendado="semanal"):
    global S
    S = create_styles()
    story = []

    emp = data["empresa"]
    editais = data["editais"]
    nome = (emp.get("nome_fantasia") or "").strip() or emp.get("razao_social", "Empresa")
    nome = fix_accents(nome)

    # Decisor from QSA
    decisor_full = emp["qsa"][0]["nome"] if emp.get("qsa") else "Prezado(a) Diretor(a)"
    decisor_full = fix_accents(decisor_full)
    honorific = detect_gender(decisor_full)
    decisor_greeting = f"{honorific} {decisor_full}"

    cnpj = emp["cnpj"]
    cnaes_sec_str = emp.get("cnaes_secundarios", "")
    n_cnaes = len([c.strip() for c in cnaes_sec_str.split(",") if c.strip()]) if cnaes_sec_str else 0
    total_cnaes = n_cnaes + 1  # principal + secondary
    capital = float(emp.get("capital_social", 0))
    CAPITAL_MULTIPLIER = 10  # ME participa de editais até 10x o capital social
    capital_threshold = capital * CAPITAL_MULTIPLIER
    capital_fmt = fmt_value_full(capital)
    setor = fix_accents(data.get("setor", ""))

    # Computed values from editais
    today = datetime.date.today()
    today_fmt = today.strftime("%d/%m/%Y")
    validity_date = today + datetime.timedelta(days=15)
    validity_fmt = validity_date.strftime("%d/%m/%Y")

    n_editais = len(editais)
    participar = [e for e in editais if e.get("recomendacao") == "PARTICIPAR"]
    avaliar = [e for e in editais if e.get("recomendacao") == "AVALIAR COM CAUTELA"]
    n_participar = len(participar)
    n_avaliar = len(avaliar)
    n_compativeis = n_participar + n_avaliar
    total_valor = sum(float(e.get("valor_estimado", 0)) for e in editais)
    total_valor_fmt = fmt_value(total_valor)
    valor_medio = total_valor / n_editais if n_editais > 0 else 0

    # Sanctions check
    sancoes = emp.get("sancoes", {})
    tem_sancao = any(sancoes.get(k) for k in ("ceis", "cnep", "cepim", "ceaf"))
    sancoes_txt = "NENHUMA (CEIS, CNEP, CEPIM, CEAF)" if not tem_sancao else "VERIFICAR — sanção detectada"

    # Municipality distribution
    mun_counter = Counter()
    mun_valor = {}
    for e in editais:
        m = fix_accents(e.get("municipio", "Desconhecido"))
        mun_counter[m] += 1
        mun_valor[m] = mun_valor.get(m, 0) + float(e.get("valor_estimado", 0))

    # Sort editais for top opportunities: PARTICIPAR first, then AVALIAR, by valor desc
    rec_order = {"PARTICIPAR": 0, "AVALIAR COM CAUTELA": 1, "NAO RECOMENDADO": 2}
    editais_sorted = sorted(editais, key=lambda e: (
        rec_order.get(e.get("recomendacao", ""), 9),
        -float(e.get("valor_estimado", 0))
    ))

    # First edital to close (soonest deadline)
    editais_by_deadline = sorted(editais, key=lambda e: e.get("data_encerramento", "9999-99-99"))
    primeiro_encerrar = editais_by_deadline[0] if editais_by_deadline else None

    # Best edital (first PARTICIPAR)
    melhor_edital = participar[0] if participar else editais_sorted[0] if editais_sorted else None

    # Resumo executivo
    resumo = data.get("resumo_executivo", {})
    resumo_texto = fix_accents(resumo.get("texto", ""))
    resumo_destaques = resumo.get("destaques", [])

    # Inteligência de mercado
    intel = data.get("inteligencia_mercado", {})

    # Próximos passos
    proximos = data.get("proximos_passos", [])

    # Company age (heuristic: not in JSON, so omit specific years)
    sede = f"{fix_accents(emp.get('cidade_sede', ''))}/{emp.get('uf_sede', '')}"

    # ==========================================================
    # CAPA
    # ==========================================================
    story.append(Spacer(1, 35 * mm))
    story.append(Paragraph("PROPOSTA DE CONSULTORIA", S['CoverTitle']))
    story.append(Paragraph("EM LICITAÇÕES PÚBLICAS", S['CoverTitle']))
    story.append(Spacer(1, 8 * mm))
    story.append(HRFlowable(width="50%", thickness=2, color=NAVY, spaceAfter=8 * mm, spaceBefore=4 * mm))
    story.append(Paragraph("Preparada exclusivamente para", S['CoverSub']))
    story.append(Paragraph(f"<b>{nome}</b>", S['CoverSub']))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(f"CNPJ: {cnpj}", S['CoverSub']))
    story.append(Spacer(1, 15 * mm))

    cover = [
        ["Data", today_fmt],
        ["Validade", f"15 dias (até {validity_fmt})"],
        ["Consultor", "Tiago Sasaki"],
        ["Contato", "(48) 9 8834-4559"],
    ]
    ct = Table([[P(a, 'CellB'), P(b, 'CellC')] for a, b in cover], colWidths=[35 * mm, 55 * mm])
    ct.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(ct)
    story.append(PageBreak())

    # ==========================================================
    # 1. CARTA AO DECISOR
    # ==========================================================
    carta_title = f"1. Carta {'à Decisora' if honorific == 'Sra.' else 'ao Decisor'}"
    story.append(Paragraph(carta_title, S['H1']))
    story.append(hr())
    story.append(Paragraph(f"{decisor_greeting},", S['BodyBold']))
    story.append(Spacer(1, 2 * mm))

    # Sector-agnostic intro (from JSON or generic fallback)
    setor_intro = fix_accents(data.get("setor_intro",
        f"Como consultor especializado em licitações públicas, acompanho diariamente o volume de "
        f"contratações no setor de {setor}. Identifico, para empresas como a {nome}, quais "
        f"oportunidades têm aderência real ao perfil técnico e financeiro da empresa."
    ))
    story.append(Paragraph(setor_intro, S['Body']))

    story.append(Paragraph(
        f"Nos últimos 30 dias, mapeei <b>{n_editais} editais em {emp.get('uf_sede', 'MG')}</b> "
        f"diretamente compatíveis com os CNAEs da {nome}, totalizando <b>{total_valor_fmt} em valor estimado</b>.",
        S['Body']
    ))
    story.append(Paragraph(
        f"O objetivo desta proposta é apresentar um diagnóstico do mercado atual e uma opção de "
        f"serviço de monitoramento contínuo que permita à {nome} participar de forma sistemática "
        f"do mercado de licitações.", S['Body']
    ))
    story.append(Paragraph(
        "Os dados são públicos. A análise é o diferencial.", S['BodyBold']
    ))
    story.append(PageBreak())

    # ==========================================================
    # 2. DIAGNÓSTICO DA EMPRESA
    # ==========================================================
    story.append(Paragraph("2. Diagnóstico da Empresa", S['H1']))
    story.append(hr())

    cnae_principal_txt = fix_accents(emp.get("cnae_principal", ""))
    story.append(make_kv([
        ["Razão Social", fix_accents(emp["razao_social"])],
        ["CNPJ", cnpj],
        ["CNAE Principal", cnae_principal_txt],
        ["CNAEs Secundários", f"{n_cnaes} CNAEs registrados"],
        ["Porte", fix_accents(emp.get("porte", ""))],
        ["Capital Social", capital_fmt],
        ["Sede", sede],
        [f"{'Sócia-Administradora' if honorific == 'Sra.' else 'Sócio-Administrador'}", decisor_full],
        ["Situação Cadastral", fix_accents(emp.get("situacao_cadastral", ""))],
        ["Sanções Gov.", sancoes_txt],
    ]))
    story.append(Spacer(1, 3 * mm))

    # Pontos Fortes — derived from data
    story.append(Paragraph("Pontos Fortes", S['H2']))
    pontos_fortes = []
    if cnae_principal_txt:
        cnae_code = cnae_principal_txt.split(" - ")[0].strip()
        cnae_desc = cnae_principal_txt.split(" - ")[1].strip() if " - " in cnae_principal_txt else cnae_principal_txt
        pontos_fortes.append(f"CNAE principal ({cnae_code}) — {fix_accents(cnae_desc)} — posiciona a empresa no setor de {setor}")

    if capital > 0:
        pct_editais = sum(1 for e in editais if float(e.get("valor_estimado", 0)) <= capital_threshold) / max(n_editais, 1) * 100
        pontos_fortes.append(f"Capital de {fmt_value(capital)} (limite de participação: {fmt_value(capital_threshold)}) — compatível com {pct_editais:.0f}% dos editais identificados")

    if n_cnaes > 5:
        pontos_fortes.append(f"{total_cnaes} CNAEs (principal + {n_cnaes} secundários) cobrem escopo amplo")

    if not tem_sancao:
        pontos_fortes.append("Empresa ativa, sem nenhuma sanção governamental")

    for pf in pontos_fortes:
        story.append(bullet(pf))

    # Pontos de Atenção — derived from data
    story.append(Paragraph("Pontos de Atenção", S['H2']))
    pontos_atencao = []

    # Capital limitation (10x multiplier)
    editais_acima_capital = sum(1 for e in editais if float(e.get("valor_estimado", 0)) > capital_threshold)
    if editais_acima_capital > 0 and capital > 0:
        pontos_atencao.append(
            f"Capital limita editais acima de {fmt_value(capital_threshold)} (10x capital social) "
            f"— {editais_acima_capital} dos {n_editais} identificados"
        )

    for pa in pontos_atencao:
        story.append(bullet(pa))

    story.append(Paragraph(
        f"A {nome} tem perfil técnico e financeiro compatível com a maioria dos editais "
        f"de {setor.lower()} em {emp.get('uf_sede', 'MG')}. "
        f"Isso representa uma oportunidade significativa de diversificação de receita.",
        S['Quote']
    ))
    story.append(PageBreak())

    # ==========================================================
    # 3. RADIOGRAFIA DO MERCADO
    # ==========================================================
    story.append(Paragraph(f"3. Radiografia do Mercado — {emp.get('uf_sede', 'MG')} {setor}", S['H1']))
    story.append(hr())

    # Big numbers
    bn = Table(
        [[P(f"{n_editais}", 'CellB'), P(f"{n_compativeis}", 'CellB'), P(total_valor_fmt, 'CellB')],
         [P("Editais mapeados"), P("Compatíveis com o perfil"), P("Valor total em disputa")]],
        colWidths=[CONTENT_W / 3] * 3,
    )
    bn.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, 0), 18),
        ('TEXTCOLOR', (0, 0), (-1, 0), NAVY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('BOX', (0, 0), (-1, -1), 1, MEDIUM_BLUE),
        ('LINEBEFORE', (1, 0), (1, -1), 0.5, MEDIUM_GRAY),
        ('LINEBEFORE', (2, 0), (2, -1), 0.5, MEDIUM_GRAY),
    ]))
    story.append(bn)
    story.append(Spacer(1, 4 * mm))

    # Distribuição por Município — dynamic
    story.append(Paragraph("Distribuição por Município", S['H2']))
    cw_mun = [48 * mm, 18 * mm, 32 * mm, 32 * mm]
    mun_rows = []
    for mun, count in mun_counter.most_common():
        valor_mun = mun_valor.get(mun, 0)
        mun_rows.append([mun, str(count), fmt_value(valor_mun), ""])
    story.append(make_table(
        ["Município", "Editais", "Valor Total", "Observação"],
        mun_rows, cw_mun
    ))
    story.append(Spacer(1, 3 * mm))

    # Tendências do Mercado — from JSON
    story.append(Paragraph("Tendências do Mercado", S['H2']))
    tendencias_raw = intel.get("tendencias", "")
    if isinstance(tendencias_raw, list):
        frases = [fix_accents(t) for t in tendencias_raw if t.strip()]
    else:
        tendencias_txt = fix_accents(tendencias_raw)
        frases = [f.strip() for f in tendencias_txt.split(". ") if f.strip()] if tendencias_txt else []
    for f in frases:
        if not f.endswith("."):
            f += "."
        story.append(bullet(f))
    story.append(PageBreak())

    # ==========================================================
    # 4. PANORAMA DO MERCADO (aggregated, no individual editais)
    # ==========================================================
    story.append(Paragraph(f"4. Panorama do Mercado — {setor}", S['H1']))
    story.append(hr())
    story.append(Paragraph(
        f"Nos últimos 30 dias, foram identificados <b>{n_editais} editais</b> compatíveis com o perfil "
        f"da {nome} em {emp.get('uf_sede', 'MG')}, totalizando <b>{total_valor_fmt} em valor estimado</b>.",
        S['Body']
    ))
    story.append(Spacer(1, 3 * mm))

    # Distribution by value range
    story.append(Paragraph("Distribuição por Faixa de Valor", S['H2']))
    faixas = {"Até R$ 500K": 0, "R$ 500K–R$ 1M": 0, "R$ 1M–R$ 5M": 0, "R$ 5M–R$ 12M": 0, "Acima de R$ 12M": 0}
    faixas_valor = {"Até R$ 500K": 0, "R$ 500K–R$ 1M": 0, "R$ 1M–R$ 5M": 0, "R$ 5M–R$ 12M": 0, "Acima de R$ 12M": 0}
    for e in editais:
        v = float(e.get("valor_estimado", 0))
        if v <= 500_000:
            k = "Até R$ 500K"
        elif v <= 1_000_000:
            k = "R$ 500K–R$ 1M"
        elif v <= 5_000_000:
            k = "R$ 1M–R$ 5M"
        elif v <= 12_000_000:
            k = "R$ 5M–R$ 12M"
        else:
            k = "Acima de R$ 12M"
        faixas[k] += 1
        faixas_valor[k] += v

    cw_faixa = [40 * mm, 25 * mm, 35 * mm, 40 * mm]
    faixa_rows = []
    for faixa, count in faixas.items():
        if count > 0:
            compat = "Compatível" if faixa != "Acima de R$ 12M" else "Avaliar consórcio"
            faixa_rows.append([faixa, str(count), fmt_value(faixas_valor[faixa]), compat])
    story.append(make_table(["Faixa de Valor", "Qtd", "Valor Total", "Compatibilidade"], faixa_rows, cw_faixa))
    story.append(Spacer(1, 3 * mm))

    # Distribution by modality
    story.append(Paragraph("Distribuição por Modalidade", S['H2']))
    mod_counter = Counter()
    mod_valor_map = {}
    for e in editais:
        m = fix_accents(e.get("modalidade", "Outras"))
        mod_counter[m] += 1
        mod_valor_map[m] = mod_valor_map.get(m, 0) + float(e.get("valor_estimado", 0))
    cw_mod = [55 * mm, 25 * mm, 40 * mm]
    mod_rows = [[mod, str(cnt), fmt_value(mod_valor_map.get(mod, 0))] for mod, cnt in mod_counter.most_common()]
    story.append(make_table(["Modalidade", "Qtd", "Valor Total"], mod_rows, cw_mod))
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph(
        f"O volume de contratações públicas em {setor.lower()} mantém ritmo constante, "
        f"com novos editais publicados semanalmente. "
        f"A empresa que monitora sistematicamente tem acesso a todas essas oportunidades "
        f"antes que os prazos se encerrem.",
        S['Quote']
    ))
    story.append(PageBreak())

    # Section 5 (Análise Detalhada) REMOVED — detailed analysis is delivered by /intel-busca

    # ==========================================================
    # 5. DIMENSIONAMENTO DA OPORTUNIDADE
    # ==========================================================
    story.append(Paragraph("5. Dimensionamento da Oportunidade", S['H1']))
    story.append(hr())

    # Valor médio por contrato
    valor_medio_fmt = fmt_value(valor_medio)
    # ROI assumptions (sector-agnostic: from JSON or default 20%)
    taxa_vitoria = data.get("taxa_vitoria_setor", 0.20)
    pct_participacao = 0.30
    editais_participados = max(1, int(n_editais * pct_participacao))
    contratos_estimados = editais_participados * taxa_vitoria
    receita_mensal = contratos_estimados * valor_medio
    receita_anual = receita_mensal * 12

    cw_loss = [CONTENT_W * 0.55, CONTENT_W * 0.45]
    story.append(make_table(
        ["Indicador", "Valor"],
        [
            [f"Editais compatíveis abertos (último mês)", str(n_editais)],
            ["Participação atual estimada", "0"],
            ["Valor total dos editais compatíveis", total_valor_fmt],
            ["Taxa média de vitória (setorial)", "20%"],
            [f"Receita potencial estimada (anual)", fmt_value(receita_anual)],
        ], cw_loss
    ))
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("Projeção em 12 Meses (cenário conservador)", S['H2']))
    cw_proj = [30 * mm, 30 * mm, 35 * mm, 40 * mm]
    # Project forward: assume same monthly rate
    story.append(make_table(
        ["Período", "Editais Est.", "Valor Est.", "Com 20% Vitória"],
        [
            ["3 meses", str(n_editais * 3), fmt_value(total_valor * 3), fmt_value(total_valor * 3 * taxa_vitoria)],
            ["6 meses", str(n_editais * 6), fmt_value(total_valor * 6), fmt_value(total_valor * 6 * taxa_vitoria)],
            ["12 meses", str(n_editais * 12), fmt_value(total_valor * 12), fmt_value(total_valor * 12 * taxa_vitoria)],
        ], cw_proj
    ))
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("Empresas COM vs SEM Monitoramento Sistemático", S['H2']))
    cw_comp = [CONTENT_W / 2] * 2
    story.append(make_table(
        ["Sem Monitoramento", "Com Monitoramento"],
        [
            ["Descobre editais por acaso ou indicação", "Recebe alertas automáticos"],
            ["Perde prazo de 60% dos editais", "Tempo adequado de preparação"],
            ["Participa de 2-3 editais/ano", "Participa de 20-30 editais/ano"],
            ["Ganha 0-1 contratos/ano", "Ganha 4-6 contratos/ano"],
            ["Depende de obra privada", "Diversifica receita com contratos públicos"],
        ], cw_comp, header_color=DARK_BLUE
    ))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        "Empresas que monitoram sistematicamente participam de 5 a 10 vezes mais editais "
        "e, consequentemente, ganham mais contratos.", S['Quote']
    ))
    story.append(PageBreak())

    # ==========================================================
    # 6. CONTEÚDO DOS RELATÓRIOS (aligned with /intel-busca real capabilities)
    # ==========================================================
    story.append(Paragraph("6. O Que Cada Relatório Entrega", S['H1']))
    story.append(hr())
    story.append(Paragraph(
        "Cada relatório é personalizado para o perfil da empresa, com dados reais "
        "e recomendações acionáveis. Top 20 editais analisados individualmente com "
        "17 campos estruturados por edital.", S['Body']
    ))

    cw_rel = [42 * mm, CONTENT_W - 42 * mm]
    story.append(make_table(
        ["Seção", "Conteúdo"],
        [
            ["Perfil da Empresa", "Dados cadastrais, CNAEs, QSA, sanções (4 bases oficiais)"],
            ["Resumo Executivo", "Métricas-chave, destaques, alertas (visão em 2 minutos)"],
            ["Top 20 Editais", "17 campos analisados por edital: objeto, requisitos, habilitação, prazos, garantias"],
            ["Análise Documental", "PDF do edital lido: requisitos técnicos, habilitação, red flags"],
            ["Recomendação", "PARTICIPAR ou NÃO PARTICIPAR com justificativa detalhada por edital"],
            ["Qualificação Econômica", "Índices contábeis exigidos, atestados específicos, garantias"],
            ["Plano de Ação", "Próximos passos priorizados com datas"],
        ], cw_rel
    ))
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("Fontes Consultadas", S['H2']))
    cw_fnt = [42 * mm, CONTENT_W - 42 * mm]
    story.append(make_table(
        ["Fonte", "Dados"],
        [
            ["PNCP", "Editais Pregão + Concorrência (fonte primária)"],
            ["PCP v2", "Editais complementares (Portal de Compras Públicas)"],
            ["OpenCNPJ", "Perfil empresarial atualizado"],
            ["Portal da Transparência", "Sanções governamentais"],
            ["PDFs dos Editais", "Extração documental (até 3 documentos por edital)"],
            ["IBGE", "População e PIB municipal (contexto geográfico)"],
        ], cw_fnt
    ))
    story.append(PageBreak())

    # ==========================================================
    # 7. PACOTES DE MONITORAMENTO
    # ==========================================================
    story.append(Paragraph("7. Pacotes de Monitoramento", S['H1']))
    story.append(hr())
    story.append(Paragraph(
        "Três opções dimensionadas para diferentes níveis de acompanhamento.", S['Body']
    ))
    story.append(Spacer(1, 2 * mm))

    cw_pkg = [55 * mm, CONTENT_W - 55 * mm]

    # --- MENSAL ---
    mensal_items = [
        ["Relatório Executivo Completo", "1x por mês"],
        ["Abrangência", f"Editais de {emp.get('uf_sede', 'SC')} (Pregão + Concorrência)"],
        ["Análise documental (PDFs)", "Até 3 editais"],
        ["Perguntas do Decisor", "Sim"],
        ["Mapa competitivo", "Sim"],
        ["Plano de ação", "Sim"],
        ["Suporte WhatsApp", "Horário comercial (seg-sex)"],
        ["Valor mensal", "R$ 997/mês"],
        ["Valor anual (pague 10, leve 12)", "R$ 9.970/ano (= R$ 831/mês)"],
    ]
    mensal_table = make_table(["Item", "Detalhe"], mensal_items, cw_pkg)
    mensal_elements = [Paragraph("Pacote Mensal", S['H2'])]
    if pacote_recomendado == "mensal":
        badge = Table([[P("RECOMENDADO", 'BadgeWhite')]], colWidths=[40 * mm])
        badge.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), NAVY),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ]))
        mensal_elements.append(badge)
        mensal_elements.append(Spacer(1, 1 * mm))
        mensal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.4, MEDIUM_GRAY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('BOX', (0, 0), (-1, -1), 2, MEDIUM_BLUE),
        ]))
    mensal_elements.append(mensal_table)
    story.append(KeepTogether(mensal_elements))
    story.append(Spacer(1, 3 * mm))

    # --- SEMANAL ---
    uf_sede = emp.get('uf_sede', 'MG')
    uf_abrangencia = data.get("uf_abrangencia", {})
    ufs_semanal = uf_abrangencia.get("semanal", [uf_sede])
    ufs_diario = uf_abrangencia.get("diario", [uf_sede])
    ufs_semanal_txt = " + ".join(ufs_semanal) if ufs_semanal else uf_sede
    ufs_diario_txt = " + ".join(ufs_diario) if ufs_diario else uf_sede

    semanal_items = [
        ["Relatório Semanal Resumido", "4x por mês (toda segunda-feira)"],
        ["Relatório Executivo Completo", "1x por mês (consolidado)"],
        ["Abrangência", ufs_semanal_txt],
        ["Análise documental (PDFs)", "Até 8 editais"],
        ["Perguntas do Decisor", "Sim"],
        ["Mapa competitivo semanal", "Sim"],
        ["Alertas de prazo crítico", "WhatsApp quando edital encerra em < 7 dias"],
        ["Suporte WhatsApp", "Horário estendido (8h-20h, seg-sáb)"],
        ["Valor mensal", "R$ 1.500/mês"],
        ["Valor anual (pague 10, leve 12)", "R$ 15.000/ano (= R$ 1.250/mês)"],
    ]
    semanal_table = make_table(["Item", "Detalhe"], semanal_items, cw_pkg)

    semanal_elements = [Paragraph("Pacote Semanal", S['H2'])]
    if pacote_recomendado == "semanal":
        badge = Table([[P("RECOMENDADO", 'BadgeWhite')]], colWidths=[40 * mm])
        badge.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), NAVY),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ]))
        semanal_elements.append(badge)
        semanal_elements.append(Spacer(1, 1 * mm))
        semanal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.4, MEDIUM_GRAY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('BOX', (0, 0), (-1, -1), 2, MEDIUM_BLUE),
        ]))
    else:
        semanal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.4, MEDIUM_GRAY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
    semanal_elements.append(semanal_table)
    story.append(KeepTogether(semanal_elements))
    story.append(Spacer(1, 3 * mm))

    # --- DIÁRIO ---
    diario_items = [
        ["Alertas diários de novos editais", "Todos os dias úteis (WhatsApp + Email)"],
        ["Relatório Semanal + Mensal", "4x semanal + 1x mensal"],
        ["Abrangência", ufs_diario_txt],
        ["Análise documental (PDFs)", "Ilimitada"],
        ["Monitoramento de concorrentes", "Sim"],
        ["Estratégia de precificação", "Sugestão de desconto por edital"],
        ["Suporte dedicado", "WhatsApp + Tel (8h-22h, seg-dom)"],
        ["Valor mensal", "R$ 2.997/mês"],
        ["Valor anual (pague 10, leve 12)", "R$ 29.970/ano (= R$ 2.498/mês)"],
    ]
    diario_table = make_table(["Item", "Detalhe"], diario_items, cw_pkg)

    diario_elements = [Paragraph("Pacote Diário", S['H2'])]
    if pacote_recomendado == "diario":
        badge = Table([[P("RECOMENDADO", 'BadgeWhite')]], colWidths=[40 * mm])
        badge.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), NAVY),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ]))
        diario_elements.append(badge)
        diario_elements.append(Spacer(1, 1 * mm))
        diario_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.4, MEDIUM_GRAY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('BOX', (0, 0), (-1, -1), 2, MEDIUM_BLUE),
        ]))
    diario_elements.append(diario_table)
    story.append(KeepTogether(diario_elements))
    story.append(Spacer(1, 3 * mm))

    # Comparativo Rápido
    story.append(Paragraph("Comparativo Rápido", S['H2']))
    cw_cmp = [40 * mm, 30 * mm, 30 * mm, 30 * mm]
    story.append(make_table(
        ["Recurso", "Mensal", "Semanal", "Diário"],
        [
            ["Relatório completo", "1x/mês", "1x/mês", "1x/mês"],
            ["Relatório resumido", "—", "4x/mês", "4x/mês"],
            ["Alertas diários", "—", "—", "Sim"],
            ["Análise de PDFs", "3", "8", "Ilimitada"],
            ["UFs monitoradas", uf_sede, ufs_semanal_txt, ufs_diario_txt],
            ["Alerta prazo crítico", "—", "Sim", "Imediato"],
            ["Monit. concorrentes", "—", "—", "Sim"],
            ["Valor mensal", "R$ 997", "R$ 1.500", "R$ 2.997"],
            ["Valor anual (10 meses)", "R$ 9.970", "R$ 15.000", "R$ 29.970"],
        ], cw_cmp
    ))
    story.append(PageBreak())

    # ==========================================================
    # 8. ROI
    # ==========================================================
    story.append(Paragraph("8. Retorno do Investimento", S['H1']))
    story.append(hr())

    # Package values for ROI calculation
    pkg_values = {"mensal": 997, "semanal": 1500, "diario": 2997}
    pkg_names = {"mensal": "Mensal", "semanal": "Semanal", "diario": "Diário"}
    investimento = pkg_values.get(pacote_recomendado, 5000)
    pkg_name = pkg_names.get(pacote_recomendado, "Semanal")

    story.append(Paragraph(
        f"Cenário Conservador — Pacote {pkg_name} (R$ {investimento:,.0f}/mês)".replace(",", "."),
        S['H2']
    ))

    roi_mensal = (receita_mensal / investimento * 100) if investimento > 0 else 0
    cw_roi = [CONTENT_W * 0.55, CONTENT_W * 0.45]
    story.append(make_table(
        ["Métrica", "Valor"],
        [
            ["Editais compatíveis identificados/mês", str(n_editais)],
            [f"Editais participados (30% do total)", f"{editais_participados}/mês"],
            ["Taxa de vitória (média setorial SC)", "20%"],
            ["Contratos estimados/mês", f"{contratos_estimados:.1f}"],
            ["Valor médio por contrato", valor_medio_fmt],
            ["Receita incremental mensal", fmt_value(receita_mensal)],
            ["Investimento mensal", f"R$ {investimento:,.0f}".replace(",", ".")],
            ["ROI mensal", f"{roi_mensal:,.0f}%".replace(",", ".")],
        ], cw_roi
    ))
    story.append(Spacer(1, 3 * mm))

    # Análise de Sensibilidade — wrapped in KeepTogether
    story.append(Paragraph("Análise de Sensibilidade", S['H2']))
    cw_sens = [32 * mm, 22 * mm, 20 * mm, 24 * mm, 26 * mm, 24 * mm]
    # Compute scenarios based on actual data
    scenarios = [
        ("Otimista", n_editais, 0.25, valor_medio * 1.4),
        ("Realista", max(1, int(n_editais * 0.6)), 0.20, valor_medio),
        ("Conservador", max(1, int(n_editais * 0.35)), 0.15, valor_medio * 0.6),
        ("Ultra-conservador", max(1, int(n_editais * 0.2)), 0.10, valor_medio * 0.3),
    ]
    sens_rows = []
    for label, ed, vit, vm in scenarios:
        rec_mes = ed * vit * vm
        roi_s = (rec_mes / investimento * 100) if investimento > 0 else 0
        sens_rows.append([label, str(ed), f"{vit:.0%}", fmt_value(vm), fmt_value(rec_mes), f"{roi_s:,.0f}%".replace(",", ".")])

    sens_table = make_table(
        ["Cenário", "Editais/mês", "Vitória", "Valor Méd.", "Receita/mês", "ROI"],
        sens_rows, cw_sens
    )
    story.append(KeepTogether([sens_table]))
    story.append(Spacer(1, 3 * mm))

    # Dynamic reference to best edital for context
    if melhor_edital:
        me_valor_n = float(melhor_edital.get("valor_estimado", 0))
        me_mun = fix_accents(melhor_edital.get("municipio", ""))
        anos_equiv = me_valor_n / (investimento * 12) if investimento > 0 else 0
        story.append(Paragraph(
            f"Mesmo no cenário mais conservador, o valor de um único contrato ganho supera em dezenas "
            f"de vezes o investimento anual no monitoramento. A título de referência: o edital de "
            f"{me_mun} ({fmt_value(me_valor_n)}) equivale a mais de {anos_equiv:.0f} anos do Pacote {pkg_name}.",
            S['Quote']
        ))
    story.append(Paragraph(
        "Projeções baseadas em dados públicos e médias setoriais. "
        "Resultados dependem da participação e execução da empresa.", S['Small']
    ))
    story.append(PageBreak())

    # ==========================================================
    # 9. QUEM ANALISA SEUS EDITAIS (Authority Section — sector-agnostic)
    # ==========================================================
    story.append(Paragraph("9. Quem Analisa Seus Editais", S['H1']))
    story.append(hr())
    story.append(Paragraph(
        "<b>Tiago Sasaki — Engenheiro e servidor público efetivo há 7 anos, "
        "com experiência direta em processos licitatórios pelo lado do órgão público.</b>",
        S['BodyBold']
    ))
    story.append(Spacer(1, 2 * mm))

    story.append(Paragraph("O Que Significa 'Do Outro Lado do Balcão'", S['H2']))
    story.append(Paragraph(
        "Nos últimos 7 anos, participei diretamente de processos licitatórios pelo lado do "
        "órgão público: elaborei termos de referência, analisei propostas de habilitação, "
        "acompanhei execuções contratuais e vi, de perto, os erros mais comuns que eliminam "
        "empresas qualificadas antes mesmo da fase de preços.",
        S['Body']
    ))
    # Authority examples: from JSON or generic fallback
    authority_items = data.get("autoridade_exemplos", [
        "Análise de centenas de propostas de habilitação — identificação dos documentos que "
        "pregoeiros verificam primeiro e onde a maioria das inabilitações acontecem",

        "Conhecimento dos critérios não escritos das comissões: como avaliam atestados, o que "
        "realmente configura 'experiência similar', e quando uma exigência é restritiva o "
        "suficiente para impugnar",

        "Acompanhamento de dezenas de contratos públicos — conhecimento de quais órgãos pagam "
        "em dia e como funciona o fluxo real de medição e pagamento",

        "Identificação de cláusulas restritivas disfarçadas em editais que pareciam limpos — "
        "requisitos de capital social desproporcionais, índices contábeis eliminatórios, "
        "exigências de atestado com quantitativos acima do razoável",
    ])
    for item in authority_items:
        story.append(bullet(fix_accents(item)))

    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("Tecnologia Proprietária", S['H2']))
    story.append(Paragraph(
        "Além da experiência como servidor, desenvolvi o SmartLic — plataforma de inteligência "
        "artificial que monitora automaticamente 3 fontes governamentais (PNCP, Portal de Compras "
        "Públicas e Portal da Transparência), classifica editais por setor e gera análises de "
        "viabilidade. Cada relatório combina varredura automatizada com análise humana de quem "
        "conhece a máquina por dentro.",
        S['Body']
    ))

    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("Diferenciais", S['H2']))
    cw_dif = [CONTENT_W / 2] * 2
    story.append(make_table(
        ["Consultoria Tradicional", "Consultoria Tiago Sasaki"],
        [
            ["Busca manual em portais", "Varredura automática diária de 3+ fontes (IA)"],
            ["Planilha genérica de editais", "Relatório personalizado — 17 campos analisados por edital"],
            ["Analista sem vivência no órgão", "7 anos como servidor — entende a lógica de quem compra"],
            ["Leitura superficial do edital", "PDF do edital lido com checklist de habilitação e red flags"],
            ["Sem filtragem setorial", "Classificação automática — zero ruído, só editais do seu setor"],
            ["Alerta genérico", "Recomendação PARTICIPAR/NÃO PARTICIPAR com justificativa detalhada"],
        ], cw_dif, header_color=DARK_BLUE
    ))
    story.append(PageBreak())

    # ==========================================================
    # 10. CONDIÇÕES COMERCIAIS
    # ==========================================================
    story.append(Paragraph("10. Condições Comerciais", S['H1']))
    story.append(hr())
    story.append(Paragraph(f"Pacote Recomendado: {pkg_name}", S['H2']))

    investimento_anual = investimento * 10  # pague 10, leve 12
    economia_anual = investimento * 2
    mensal_anual = investimento_anual / 12

    inv_fmt = f"{investimento:,.0f}".replace(",", ".")
    inv_anual_fmt = f"{investimento_anual:,.0f}".replace(",", ".")
    eco_fmt = f"{economia_anual:,.0f}".replace(",", ".")
    story.append(make_kv([
        ["Pacote", pkg_name],
        ["Investimento mensal", f"R$ {inv_fmt}/mês"],
        ["Pagamento anual adiantado", f"R$ {inv_anual_fmt}/ano (pague 10, leve 12)"],
        ["Economia no plano anual", f"R$ {eco_fmt} (2 meses de cortesia)"],
        ["Forma de pagamento", "Boleto, PIX ou Cartão de Crédito"],
        ["Prazo mínimo", "3 meses"],
        ["Cancelamento", "30 dias de antecedência"],
        ["Início", "Imediato após aceite"],
        ["Primeiro relatório", "Até 3 dias úteis após contratação"],
    ], kw=52 * mm))
    story.append(Spacer(1, 4 * mm))

    # C3: Condição Especial — visual highlight box
    cond_especial_elements = []
    cond_especial_elements.append(Spacer(1, 2 * mm))

    oferta_label = Table(
        [[P("OFERTA POR TEMPO LIMITADO", 'BadgeWhite')]],
        colWidths=[60 * mm]
    )
    oferta_label.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NAVY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    cond_especial_elements.append(oferta_label)
    cond_especial_elements.append(Spacer(1, 2 * mm))

    # Generic urgency — no specific edital dates
    cond_text = (
        f"Para contratações formalizadas até <b>{validity_fmt}</b>, o primeiro mês de monitoramento "
        f"é cortesia, permitindo que a empresa já receba o primeiro relatório completo com "
        f"os editais abertos no setor de {setor.lower()}."
    )

    cond_inner = Table(
        [[Paragraph(cond_text, S['Body'])]],
        colWidths=[CONTENT_W - 12 * mm]
    )
    cond_inner.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE),
        ('BOX', (0, 0), (-1, -1), 2, MEDIUM_BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    cond_especial_elements.append(cond_inner)
    cond_especial_elements.append(Spacer(1, 1 * mm))
    cond_especial_elements.append(Paragraph(
        f"Após esta data, a condição padrão se aplica.", S['Small']
    ))

    story.append(KeepTogether(cond_especial_elements))
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("O Que NÃO Está Incluído", S['H2']))
    for item in [
        "Elaboração de propostas comerciais (documentos de habilitação são responsabilidade da empresa)",
        "Representação presencial em sessões de licitação",
        "Serviços jurídicos (impugnações, recursos)",
        "Execução do objeto contratado",
        "Garantias financeiras",
    ]:
        story.append(bullet(item))
    story.append(Paragraph(
        "Estes serviços podem ser contratados separadamente sob demanda.", S['Small']
    ))
    story.append(PageBreak())

    # ==========================================================
    # 11. PRÓXIMOS PASSOS
    # ==========================================================
    story.append(Paragraph("11. Próximos Passos", S['H1']))
    story.append(hr())

    # Resumo Executivo (from JSON)
    if resumo_texto:
        story.append(Paragraph("Resumo Executivo", S['H2']))
        story.append(Paragraph(resumo_texto, S['Body']))
        if resumo_destaques:
            for d in resumo_destaques:
                story.append(bullet(fix_accents(d)))
        story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("Após Aceite", S['H2']))
    cw_steps = [30 * mm, 22 * mm, CONTENT_W - 52 * mm]
    story.append(make_table(
        ["Etapa", "Quando", "O Que Acontece"],
        [
            ["Aceite", "Dia 0", "Confirmação via WhatsApp ou email"],
            ["Onboarding", "Dia 1-2", "Alinhamento: UFs, faixa de valor, tipos de contratação"],
            ["Primeiro Relatório", "Dia 3-5", "Relatório completo + plano de ação"],
            ["Monitoramento", "Dia 6+", "Relatórios na frequência contratada"],
        ], cw_steps
    ))
    story.append(Spacer(1, 4 * mm))

    # C2: CTA Box — high-conversion (no specific edital dates)
    cta_box = Table(
        [
            [Paragraph("Responda agora pelo WhatsApp: (48) 9 8834-4559", S['CTAWhite'])],
            [Paragraph("ou envie um email para tiago.sasaki@confenge.com.br", S['CTAWhiteSub'])],
        ],
        colWidths=[CONTENT_W],
    )
    cta_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NAVY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (0, 0), 10),
        ('BOTTOMPADDING', (-1, -1), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
    ]))
    story.append(cta_box)
    story.append(Spacer(1, 3 * mm))

    # Generic urgency (no specific edital reference)
    story.append(Paragraph(
        f"Novos editais são publicados semanalmente. Cada semana sem monitoramento "
        f"é um conjunto de editais compatíveis que passa sem que a {nome} sequer saiba que existiram.",
        S['Quote']
    ))

    story.append(Spacer(1, 3 * mm))

    # Próximos Passos table from JSON
    if proximos:
        story.append(Paragraph("Plano de Ação Recomendado", S['H2']))
        cw_prox = [CONTENT_W * 0.50, 30 * mm, 25 * mm]
        prox_rows = []
        for p in proximos:
            prox_rows.append([
                fix_accents(p.get("acao", "")),
                fix_accents(p.get("prazo", "")),
                fix_accents(p.get("prioridade", "")),
            ])
        story.append(make_table(["Ação", "Prazo", "Prioridade"], prox_rows, cw_prox))
        story.append(Spacer(1, 3 * mm))

    story.append(Paragraph(
        "Os prazos acima são reais e públicos. A decisão de acompanhar ou não o "
        "mercado de licitações é estratégica, e o momento ideal para iniciar é "
        "enquanto ainda há editais abertos compatíveis com o perfil da empresa.", S['Quote']
    ))
    story.append(Spacer(1, 6 * mm))

    # Contact block
    story.append(HRFlowable(width="40%", thickness=1, color=NAVY, spaceAfter=4 * mm, spaceBefore=4 * mm))
    story.append(Paragraph("<b>Tiago Sasaki</b>", S['Body']))
    story.append(Paragraph("Engenheiro | Servidor Efetivo — SIE/SC", S['Body']))
    story.append(Paragraph("Consultor de Licitações | CONFENGE", S['Body']))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("<b>WhatsApp:</b> (48) 9 8834-4559", S['Body']))
    story.append(Paragraph("<b>Email:</b> tiago.sasaki@confenge.com.br", S['Body']))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "Disponível para uma conversa sem compromisso para esclarecer qualquer ponto desta proposta.",
        S['Body']
    ))
    story.append(Spacer(1, 8 * mm))

    # Disclaimer
    story.append(Paragraph(
        f"Proposta preparada com dados reais de editais abertos em {today_fmt}. "
        f"Informações extraídas de fontes públicas oficiais (PNCP, Portal da "
        f"Transparência, OpenCNPJ). Projeções de ROI são estimativas baseadas em "
        f"médias setoriais; resultados dependem da participação e execução da empresa.",
        S['Small']
    ))

    # ==========================================================
    # BUILD
    # ==========================================================
    def on_page(canvas, doc):
        canvas.saveState()
        # Footer
        canvas.setFont('Helvetica', 7.5)
        canvas.setFillColor(HexColor("#a0aec0"))
        canvas.drawCentredString(PAGE_W / 2, 10 * mm, FOOTER_TEXT)
        canvas.drawRightString(PAGE_W - MARGIN, 10 * mm, f"Página {doc.page}")
        # Top line
        canvas.setStrokeColor(MEDIUM_BLUE)
        canvas.setLineWidth(0.4)
        canvas.line(MARGIN, PAGE_H - 14 * mm, PAGE_W - MARGIN, PAGE_H - 14 * mm)
        canvas.restoreState()

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=18 * mm, bottomMargin=18 * mm,
    )
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"PDF gerado: {output_path}")
    print(f"Páginas: ~{doc.page}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gerador de PDF de Proposta Comercial B2G v3"
    )
    parser.add_argument(
        "input_positional", nargs="?", default=None,
        help="Caminho do JSON de dados (argumento posicional, alternativa a --input)"
    )
    parser.add_argument(
        "output_positional", nargs="?", default=None,
        help="Caminho do PDF de saída (argumento posicional, alternativa a --output)"
    )
    parser.add_argument(
        "--input", "-i", dest="input_file", default=None,
        help="Caminho do JSON de dados"
    )
    parser.add_argument(
        "--output", "-o", dest="output_file", default=None,
        help="Caminho do PDF de saída"
    )
    parser.add_argument(
        "--pacote", "-p", choices=["mensal", "semanal", "diario"], default="semanal",
        help="Pacote recomendado a destacar (default: semanal)"
    )

    args = parser.parse_args()

    # Resolve input: --input takes precedence over positional
    data_path = args.input_file or args.input_positional or "docs/reports/data-27232335000191-2026-03-11.json"
    output_path = args.output_file or args.output_positional or "docs/propostas/proposta-output.pdf"

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    build_pdf(data, output_path, pacote_recomendado=args.pacote)
