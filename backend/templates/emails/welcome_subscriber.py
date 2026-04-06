"""Welcome email for new subscribers (Zero-churn P1 8.1).

Sent after checkout.session.completed webhook activates a subscription.
Confirms the subscription is active and provides next steps.
"""

from templates.emails.base import email_base, SMARTLIC_GREEN, FRONTEND_URL


def render_welcome_subscriber_email(
    user_name: str,
    plan_name: str = "SmartLic Pro",
) -> str:
    """Render welcome email for new paid subscriber.

    Args:
        user_name: User's display name.
        plan_name: Plan name (e.g., "SmartLic Pro", "Consultoria").
    """
    preheader = f"Sua assinatura {plan_name} esta ativa! Veja os proximos passos."

    body = f"""
    <div style="display:none;font-size:1px;color:#f4f4f4;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;">{preheader}</div>

    <h1 style="color: #333; font-size: 22px; margin: 0 0 16px;">
      Bem-vindo ao {plan_name}!
    </h1>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      Ola, {user_name}! Sua assinatura esta ativa e voce agora tem acesso
      completo a todas as funcionalidades do SmartLic.
    </p>

    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
           style="background-color: #e8f5e9; border-radius: 8px; padding: 20px; margin: 0 0 24px;">
      <tr>
        <td style="padding: 16px;">
          <p style="color: #1b5e20; font-size: 15px; margin: 0 0 16px; font-weight: 600;">
            Proximos passos para aproveitar ao maximo:
          </p>
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="padding: 8px 0; color: #555; font-size: 14px; border-bottom: 1px solid rgba(0,0,0,0.06);">
                <strong style="color: {SMARTLIC_GREEN}; font-size: 18px; margin-right: 8px;">1.</strong>
                <a href="{FRONTEND_URL}/buscar" style="color: #333; text-decoration: none; font-weight: 500;">
                  Faca buscas ilimitadas
                </a>
                <br/><span style="color: #888; font-size: 13px; margin-left: 26px;">Todos os resultados desbloqueados, sem preview</span>
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0; color: #555; font-size: 14px; border-bottom: 1px solid rgba(0,0,0,0.06);">
                <strong style="color: {SMARTLIC_GREEN}; font-size: 18px; margin-right: 8px;">2.</strong>
                <a href="{FRONTEND_URL}/pipeline" style="color: #333; text-decoration: none; font-weight: 500;">
                  Organize seu pipeline
                </a>
                <br/><span style="color: #888; font-size: 13px; margin-left: 26px;">Pipeline ilimitado para acompanhar oportunidades</span>
              </td>
            </tr>
            <tr>
              <td style="padding: 8px 0; color: #555; font-size: 14px;">
                <strong style="color: {SMARTLIC_GREEN}; font-size: 18px; margin-right: 8px;">3.</strong>
                <a href="{FRONTEND_URL}/buscar" style="color: #333; text-decoration: none; font-weight: 500;">
                  Exporte relatorios Excel
                </a>
                <br/><span style="color: #888; font-size: 13px; margin-left: 26px;">Relatorios completos para compartilhar com sua equipe</span>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>

    <p style="text-align: center; margin: 24px 0 16px;">
      <a href="{FRONTEND_URL}/buscar"
         style="display: inline-block; padding: 14px 32px; background-color: {SMARTLIC_GREEN}; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
        Comecar a buscar
      </a>
    </p>

    <p style="color: #888; font-size: 13px; text-align: center; margin: 16px 0 0;">
      Duvidas? Responda este email ou acesse <a href="{FRONTEND_URL}/ajuda" style="color: {SMARTLIC_GREEN};">nossa central de ajuda</a>.
    </p>
    """

    return email_base(
        title=f"Bem-vindo ao {plan_name}!",
        body_html=body,
        is_transactional=True,
    )
