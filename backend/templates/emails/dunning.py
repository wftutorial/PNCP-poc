"""
Dunning email templates — STORY-309 AC2

Six dunning templates covering the full payment failure recovery sequence:

  render_dunning_friendly_email   — Day 0,  attempt 1 (tone: empathetic / friendly)
  render_dunning_reminder_email   — Day 3,  attempt 2 (tone: gentle reminder)
  render_dunning_urgent_email     — Day 7,  attempt 3 (tone: urgent)
  render_dunning_final_email      — Day 14, attempt 4 (tone: final warning)
  render_dunning_recovery_email   — After payment succeeds during dunning (celebratory)
  render_pre_dunning_email        — 7 days before card expiry (informative)

AC2 requirements:
  - Include user name, plan, value, failure reason (where applicable).
  - Show days remaining until cancellation (countdown).
  - CTA: "Atualizar Forma de Pagamento" → Stripe Billing Portal URL.
  - Tone: empathetic, no blame ("você deve"), direct ("pagamento falhou").
  - Sender display: "Tiago from SmartLic" (set in email_service.py — not here).
"""

from templates.emails.base import email_base, SMARTLIC_GREEN, FRONTEND_URL

# Colors used across dunning templates
_URGENT_RED = "#d32f2f"
_FINAL_RED = "#b71c1c"
_WARNING_ORANGE = "#e65100"


# ---------------------------------------------------------------------------
# Helper — shared payment details table block
# ---------------------------------------------------------------------------

def _payment_details_table(
    plan_name: str,
    amount: str,
    failure_reason: str | None,
    bg_color: str = "#fef8f8",
    border_color: str = "#ffebee",
) -> str:
    """Render a two-column details table (plan, amount, optionally failure reason)."""
    reason_row = ""
    if failure_reason:
        reason_row = f"""
            <tr>
              <td style="color: #888; font-size: 13px; padding: 6px 0;">Motivo</td>
              <td align="right" style="color: {_URGENT_RED}; font-size: 14px; padding: 6px 0;">{failure_reason}</td>
            </tr>"""

    return f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
           style="background-color: {bg_color}; border-radius: 8px; border: 1px solid {border_color}; margin: 0 0 24px;">
      <tr>
        <td style="padding: 20px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="color: #888; font-size: 13px; padding: 6px 0;">Plano</td>
              <td align="right" style="color: #333; font-size: 15px; font-weight: 600; padding: 6px 0;">{plan_name}</td>
            </tr>
            <tr>
              <td style="color: #888; font-size: 13px; padding: 6px 0;">Valor</td>
              <td align="right" style="color: #333; font-size: 15px; font-weight: 600; padding: 6px 0;">{amount}</td>
            </tr>{reason_row}
          </table>
        </td>
      </tr>
    </table>"""


def _cta_button(billing_portal_url: str, label: str = "Atualizar Forma de Pagamento", bg_color: str = _URGENT_RED) -> str:
    """Render the primary CTA button pointing to the Stripe Billing Portal."""
    return f"""
    <p style="text-align: center; margin: 24px 0 16px;">
      <a href="{billing_portal_url}"
         class="btn"
         style="display: inline-block; padding: 14px 32px; background-color: {bg_color}; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
        {label}
      </a>
    </p>"""


def _days_text(days_remaining: int) -> str:
    return "1 dia" if days_remaining == 1 else f"{days_remaining} dias"


# ---------------------------------------------------------------------------
# 1. Day 0 — Attempt 1: Friendly
# ---------------------------------------------------------------------------

def render_dunning_friendly_email(
    user_name: str,
    plan_name: str,
    amount: str,
    failure_reason: str,
    billing_portal_url: str,
) -> str:
    """
    Dunning Day 0 — attempt 1.

    Tone: friendly, empathetic. "Isso acontece — vamos resolver rapidinho."
    Sender display: "Tiago from SmartLic" (set in email_service.py).

    Args:
        user_name: User's display name.
        plan_name: Current plan name (e.g. "SmartLic Pro").
        amount: Formatted amount (e.g. "R$ 397,00").
        failure_reason: Human-readable Stripe decline reason.
        billing_portal_url: Direct URL to Stripe Billing Portal session.
    """
    body = f"""
    <h1 style="color: #333; font-size: 22px; margin: 0 0 16px;">
      Houve um problema com seu pagamento
    </h1>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      Olá, {user_name}! Tudo bem? Detectamos que o pagamento da sua assinatura
      <strong>{plan_name}</strong> não foi processado. Isso acontece — vamos resolver rapidinho.
    </p>

    {_payment_details_table(plan_name, amount, failure_reason, bg_color="#fef8f8", border_color="#ffebee")}

    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 24px;">
      Basta atualizar sua forma de pagamento pelo botão abaixo. Leva menos de 1 minuto
      e sua assinatura continua normalmente, sem interrupção.
    </p>

    {_cta_button(billing_portal_url, bg_color=SMARTLIC_GREEN)}

    <p style="color: #888; font-size: 14px; line-height: 1.6; margin: 24px 0 0;">
      Se tiver dúvidas, responda este email — estamos aqui para ajudar.
    </p>
    """

    return email_base(
        title="Problema com seu pagamento — SmartLic",
        body_html=body,
        is_transactional=True,
    )


# ---------------------------------------------------------------------------
# 2. Day 3 — Attempt 2: Gentle reminder
# ---------------------------------------------------------------------------

def render_dunning_reminder_email(
    user_name: str,
    plan_name: str,
    amount: str,
    days_remaining: int,
    billing_portal_url: str,
) -> str:
    """
    Dunning Day 3 — attempt 2.

    Tone: gentle reminder. "Ação necessária: atualize seu pagamento."
    Shows countdown of days remaining before cancellation.
    Sender display: "Tiago from SmartLic" (set in email_service.py).

    Args:
        user_name: User's display name.
        plan_name: Current plan name.
        amount: Formatted amount (e.g. "R$ 397,00").
        days_remaining: Days left before subscription is cancelled.
        billing_portal_url: Direct URL to Stripe Billing Portal session.
    """
    days = _days_text(days_remaining)

    body = f"""
    <h1 style="color: #e65100; font-size: 22px; margin: 0 0 16px;">
      Lembrete: pagamento pendente
    </h1>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      Olá, {user_name}! Ainda não conseguimos processar o pagamento da sua assinatura
      <strong>{plan_name}</strong> no valor de <strong>{amount}</strong>.
    </p>

    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
           style="background-color: #fff8f0; border-radius: 8px; border: 1px solid #ffe0b2; margin: 0 0 24px;">
      <tr>
        <td style="padding: 20px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="color: #888; font-size: 13px; padding: 6px 0;">Plano</td>
              <td align="right" style="color: #333; font-size: 15px; font-weight: 600; padding: 6px 0;">{plan_name}</td>
            </tr>
            <tr>
              <td style="color: #888; font-size: 13px; padding: 6px 0;">Valor</td>
              <td align="right" style="color: #333; font-size: 15px; font-weight: 600; padding: 6px 0;">{amount}</td>
            </tr>
            <tr>
              <td style="color: #888; font-size: 13px; padding: 6px 0;">Prazo para regularizar</td>
              <td align="right" style="color: {_WARNING_ORANGE}; font-size: 15px; font-weight: 700; padding: 6px 0;">{days}</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>

    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 24px;">
      Atualize sua forma de pagamento antes que o prazo expire para manter o acesso
      completo ao SmartLic.
    </p>

    {_cta_button(billing_portal_url, bg_color=_WARNING_ORANGE)}

    <p style="color: #888; font-size: 14px; line-height: 1.6; margin: 24px 0 0;">
      Dificuldades? Responda este email — vamos te ajudar a resolver.
    </p>
    """

    return email_base(
        title=f"Pagamento pendente — {days} restantes — SmartLic",
        body_html=body,
        is_transactional=True,
    )


# ---------------------------------------------------------------------------
# 3. Day 7 — Attempt 3: Urgent
# ---------------------------------------------------------------------------

def render_dunning_urgent_email(
    user_name: str,
    plan_name: str,
    amount: str,
    days_remaining: int,
    billing_portal_url: str,
) -> str:
    """
    Dunning Day 7 — attempt 3.

    Tone: urgent. "Sua assinatura está em risco — X dias restantes."
    Uses red urgency color to signal serious risk.
    Sender display: "Tiago from SmartLic" (set in email_service.py).

    Args:
        user_name: User's display name.
        plan_name: Current plan name.
        amount: Formatted amount (e.g. "R$ 397,00").
        days_remaining: Days left before subscription is cancelled.
        billing_portal_url: Direct URL to Stripe Billing Portal session.
    """
    days = _days_text(days_remaining)

    body = f"""
    <h1 style="color: {_URGENT_RED}; font-size: 22px; margin: 0 0 16px;">
      Sua assinatura está em risco — {days} restantes
    </h1>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      Olá, {user_name}! O pagamento da sua assinatura <strong>{plan_name}</strong>
      continua em aberto. Se não for regularizado em <strong style="color: {_URGENT_RED};">{days}</strong>,
      sua conta será suspensa automaticamente.
    </p>

    {_payment_details_table(plan_name, amount, failure_reason=None, bg_color="#fef8f8", border_color="#ffcdd2")}

    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
           style="background-color: #fef8f8; border-left: 4px solid {_URGENT_RED}; border-radius: 0 8px 8px 0; margin: 0 0 24px; padding: 0;">
      <tr>
        <td style="padding: 16px 20px;">
          <p style="color: {_URGENT_RED}; font-size: 15px; font-weight: 600; margin: 0 0 4px;">O que acontece se eu não atualizar?</p>
          <p style="color: #555; font-size: 14px; line-height: 1.6; margin: 0;">
            Após {days}, o acesso ao SmartLic será suspenso e você deixará de receber
            alertas de licitações, análises de viabilidade e relatórios.
          </p>
        </td>
      </tr>
    </table>

    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 24px;">
      Atualize agora — leva menos de 1 minuto e sua conta volta ao normal imediatamente.
    </p>

    {_cta_button(billing_portal_url, bg_color=_URGENT_RED)}

    <p style="color: #888; font-size: 14px; line-height: 1.6; margin: 24px 0 0;">
      Precisa de ajuda? Responda este email diretamente.
    </p>
    """

    return email_base(
        title=f"Urgente: assinatura em risco — {days} — SmartLic",
        body_html=body,
        is_transactional=True,
    )


# ---------------------------------------------------------------------------
# 4. Day 14 — Attempt 4: Final warning
# ---------------------------------------------------------------------------

def render_dunning_final_email(
    user_name: str,
    plan_name: str,
    amount: str,
    billing_portal_url: str,
) -> str:
    """
    Dunning Day 14 — attempt 4 (final warning).

    Tone: final, high urgency. "Aviso final: sua conta será suspensa amanhã."
    Uses dark red to signal imminent suspension.
    Sender display: "Tiago from SmartLic" (set in email_service.py).

    Args:
        user_name: User's display name.
        plan_name: Current plan name.
        amount: Formatted amount (e.g. "R$ 397,00").
        billing_portal_url: Direct URL to Stripe Billing Portal session.
    """
    body = f"""
    <h1 style="color: {_FINAL_RED}; font-size: 22px; margin: 0 0 16px;">
      Aviso final: sua conta será suspensa amanhã
    </h1>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      Olá, {user_name}. Este é o último aviso sobre o pagamento em aberto
      da sua assinatura <strong>{plan_name}</strong>.
    </p>

    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
           style="background-color: #fef2f2; border-radius: 8px; border: 2px solid {_FINAL_RED}; margin: 0 0 24px;">
      <tr>
        <td style="padding: 20px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="color: #888; font-size: 13px; padding: 6px 0;">Plano</td>
              <td align="right" style="color: #333; font-size: 15px; font-weight: 600; padding: 6px 0;">{plan_name}</td>
            </tr>
            <tr>
              <td style="color: #888; font-size: 13px; padding: 6px 0;">Valor</td>
              <td align="right" style="color: #333; font-size: 15px; font-weight: 600; padding: 6px 0;">{amount}</td>
            </tr>
            <tr>
              <td style="color: #888; font-size: 13px; padding: 6px 0;">Suspensão em</td>
              <td align="right" style="color: {_FINAL_RED}; font-size: 15px; font-weight: 700; padding: 6px 0;">AMANHÃ</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>

    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      Se o pagamento não for regularizado hoje, sua conta será suspensa e você perderá
      acesso a buscas, alertas, pipeline de oportunidades e todos os seus dados históricos.
    </p>

    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 24px;">
      Atualize agora para manter o acesso:
    </p>

    {_cta_button(billing_portal_url, bg_color=_FINAL_RED)}

    <p style="color: #888; font-size: 14px; line-height: 1.6; margin: 24px 0 0;">
      Se já resolveu o problema ou acredita que há um erro, responda este email imediatamente.
    </p>
    """

    return email_base(
        title="Aviso final: conta suspensa amanhã — SmartLic",
        body_html=body,
        is_transactional=True,
    )


# ---------------------------------------------------------------------------
# 5. Recovery — Payment succeeded after dunning
# ---------------------------------------------------------------------------

def render_dunning_recovery_email(
    user_name: str,
    plan_name: str,
) -> str:
    """
    Sent when payment is successfully recovered during the dunning sequence.

    Tone: celebratory, relieved. "Pagamento restaurado com sucesso!"
    Uses green color scheme to signal positive outcome.
    Sender display: "Tiago from SmartLic" (set in email_service.py).

    Args:
        user_name: User's display name.
        plan_name: Current plan name.
    """
    body = f"""
    <h1 style="color: {SMARTLIC_GREEN}; font-size: 22px; margin: 0 0 16px;">
      Pagamento restaurado com sucesso!
    </h1>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      Olá, {user_name}! Ótima notícia — o pagamento da sua assinatura
      <strong>{plan_name}</strong> foi processado com sucesso.
    </p>

    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
           style="background-color: #f8faf8; border-radius: 8px; border: 1px solid #e8f5e9; margin: 0 0 24px;">
      <tr>
        <td style="padding: 20px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="color: #888; font-size: 13px; padding: 6px 0;">Status</td>
              <td align="right" style="color: {SMARTLIC_GREEN}; font-size: 15px; font-weight: 700; padding: 6px 0;">Ativo</td>
            </tr>
            <tr>
              <td style="color: #888; font-size: 13px; padding: 6px 0;">Plano</td>
              <td align="right" style="color: #333; font-size: 15px; font-weight: 600; padding: 6px 0;">{plan_name}</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>

    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 24px;">
      Sua conta está ativa e todas as funcionalidades estão disponíveis normalmente.
      Continue encontrando as melhores licitações para o seu negócio!
    </p>

    <p style="text-align: center; margin: 24px 0 16px;">
      <a href="{FRONTEND_URL}/buscar"
         class="btn"
         style="display: inline-block; padding: 14px 32px; background-color: {SMARTLIC_GREEN}; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
        Continuar buscando licitações
      </a>
    </p>

    <p style="color: #888; font-size: 14px; line-height: 1.6; margin: 24px 0 0;">
      Obrigado por ficar com a gente. Qualquer dúvida, estamos aqui.
    </p>
    """

    return email_base(
        title="Pagamento restaurado — SmartLic",
        body_html=body,
        is_transactional=True,
    )


# ---------------------------------------------------------------------------
# 6. Pre-dunning — Card expiring in 7 days
# ---------------------------------------------------------------------------

def render_pre_dunning_email(
    user_name: str,
    card_last4: str,
    card_exp_month: int,
    card_exp_year: int,
    billing_portal_url: str,
) -> str:
    """
    Sent 7 days before the user's card expires to prevent future payment failures.

    Tone: informative, proactive. "Seu cartão termina em MM/AA — atualize antes da próxima cobrança."
    Sender display: "Tiago from SmartLic" (set in email_service.py).

    Args:
        user_name: User's display name.
        card_last4: Last 4 digits of the expiring card.
        card_exp_month: Card expiry month (1–12).
        card_exp_year: Card expiry year (e.g. 2026).
        billing_portal_url: Direct URL to Stripe Billing Portal session.
    """
    exp_month_str = str(card_exp_month).zfill(2)
    exp_year_str = str(card_exp_year)[-2:]  # e.g. 2026 → "26"
    exp_display = f"{exp_month_str}/{exp_year_str}"

    body = f"""
    <h1 style="color: #333; font-size: 22px; margin: 0 0 16px;">
      Seu cartão termina em {exp_display} — atualize antes da próxima cobrança
    </h1>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      Olá, {user_name}! O cartão com final <strong>•••• {card_last4}</strong> registrado
      na sua conta expira em <strong>{exp_display}</strong>.
    </p>

    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
           style="background-color: #fffde7; border-radius: 8px; border: 1px solid #fff9c4; margin: 0 0 24px;">
      <tr>
        <td style="padding: 20px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="color: #888; font-size: 13px; padding: 6px 0;">Cartão</td>
              <td align="right" style="color: #333; font-size: 15px; font-weight: 600; padding: 6px 0;">•••• {card_last4}</td>
            </tr>
            <tr>
              <td style="color: #888; font-size: 13px; padding: 6px 0;">Expira em</td>
              <td align="right" style="color: #e65100; font-size: 15px; font-weight: 700; padding: 6px 0;">{exp_display}</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>

    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 24px;">
      Para evitar interrupção na sua assinatura, cadastre um novo cartão agora.
      Leva menos de 1 minuto e garante que sua próxima cobrança seja processada sem problemas.
    </p>

    {_cta_button(billing_portal_url, label="Atualizar Forma de Pagamento", bg_color=SMARTLIC_GREEN)}

    <p style="color: #888; font-size: 14px; line-height: 1.6; margin: 24px 0 0;">
      Se tiver dúvidas, responda este email — estamos aqui para ajudar.
    </p>
    """

    return email_base(
        title=f"Cartão expira em {exp_display} — atualize antes da próxima cobrança",
        body_html=body,
        is_transactional=True,
    )
