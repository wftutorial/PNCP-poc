"""Day-3 Share Activation — SEO-PLAYBOOK §7.1 / P6 (L1275).

Fires on Day-3 of trial for users who have analyzed editais
(stats.opportunities_found > 0) but have NOT shared any analysis yet.
Completes the viral loop: analyst analyzes → shares with decision maker →
decision maker converts. KPI (playbook L828): 150 shares/month × 20%
conversion = 30 viral trials/month, CAC ≈ 0.

Filter logic is applied in services.trial_email_sequence.process_trial_emails:
  - Skip if opportunities_found == 0 (nothing to share yet — wait for
    analysis to happen before asking to share).
  - Skip if user already has ≥1 row in `shared_analyses` (goal achieved).

The email is intentionally different from the Day-7 `referral_invitation`
(that one is about inviting strangers to trial; this one is about sharing
a specific edital analysis with an internal decision maker). Both can be
active simultaneously because they target different funnel stages.
"""

from templates.emails.base import email_base, SMARTLIC_GREEN, FRONTEND_URL


def render_share_activation_email(
    user_name: str,
    opportunities_found: int = 0,
    unsubscribe_url: str = "",
) -> str:
    """Render the Day-3 share activation HTML email.

    Args:
        user_name: Display name for the greeting.
        opportunities_found: Count of opportunities the user already analyzed,
            used to personalize the body (the "why" for sharing).
        unsubscribe_url: RFC 8058 one-click unsubscribe URL.

    Returns:
        Full HTML email body wrapped by ``email_base``.
    """
    # Humanized count phrasing — graceful when the number is absent or zero.
    if opportunities_found > 1:
        analyzed_phrase = (
            f"Você já analisou <strong>{opportunities_found} oportunidades</strong> no SmartLic."
        )
    elif opportunities_found == 1:
        analyzed_phrase = "Você já analisou <strong>1 oportunidade</strong> no SmartLic."
    else:
        analyzed_phrase = "Você já usou o SmartLic para analisar editais."

    body = f"""
    <h1 style="color: #333; font-size: 24px; margin: 0 0 16px;">
      {user_name}, seu score pode acelerar a decisão do seu diretor
    </h1>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      {analyzed_phrase} A parte mais difícil — filtrar, ler e pontuar —
      já foi feita. Falta apenas o passo final: o decisor olhar para o
      score e autorizar a participação.
    </p>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      <strong>Compartilhe uma análise em 1 clique.</strong> O link leva
      para uma página pública com o score de viabilidade, o breakdown
      dos 4 fatores (modalidade, prazo, valor, geografia) e o resumo do
      edital. Seu diretor não precisa de conta, login, nem instalação —
      clica no WhatsApp, vê o número, decide.
    </p>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 24px;">
      É o funil mais curto de B2B: quem analisa compartilha com quem
      decide — e a decisão acontece na mesma conversa. Equipes que
      usam essa rotina reduzem o tempo entre "encontrei o edital" e
      "vamos participar" de 3 dias para 30 minutos.
    </p>

    <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: 0 auto 16px;">
      <tr>
        <td align="center" style="background: {SMARTLIC_GREEN}; border-radius: 8px;">
          <a href="{FRONTEND_URL}/buscar"
             style="display: inline-block; padding: 14px 28px; color: #fff;
                    text-decoration: none; font-weight: 600; font-size: 16px;">
            Ver minhas análises e compartilhar →
          </a>
        </td>
      </tr>
    </table>

    <p style="color: #888; font-size: 13px; line-height: 1.5; margin: 24px 0 0;">
      Como funciona: em qualquer resultado de busca, clique no botão
      "Compartilhar análise". O link é público por 30 dias e cada
      visualização é rastreada. Use no WhatsApp, email ou Slack do time.
    </p>
    """
    return email_base(
        title="Seu score pode acelerar a decisão do seu diretor",
        body_html=body,
        unsubscribe_url=unsubscribe_url,
        is_transactional=False,
    )
