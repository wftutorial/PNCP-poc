"""Day-3 Activation Nudge — SEO-PLAYBOOK §Day-3 Activation.

Fires on Day-2 of trial for users who have NOT yet completed their first
search (stats.searches_count == 0). Day-3 activation rate is the single
strongest predictor of trial→paid conversion (playbook L1053-1066 and
industry data from 2026: users reaching "aha moment" in first 3 days
convert 4x more than users who reach it after Day-7).

The email is deliberately short and action-oriented — the only goal is to
get the user back into /buscar to execute their first real search. No
feature explanation, no social proof, no pricing — just the CTA.
"""

from templates.emails.base import email_base, SMARTLIC_GREEN, FRONTEND_URL


def render_day3_activation_email(
    user_name: str,
    unsubscribe_url: str = "",
) -> str:
    """Render the Day-3 activation nudge HTML email.

    Args:
        user_name: Display name for the greeting.
        unsubscribe_url: RFC 8058 one-click unsubscribe URL.

    Returns:
        Full HTML email body wrapped by ``email_base``.
    """
    body = f"""
    <h1 style="color: #333; font-size: 24px; margin: 0 0 16px;">
      Sua primeira análise está a 30 segundos, {user_name}
    </h1>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      Você criou sua conta no SmartLic há dois dias — e ainda não rodou sua
      primeira busca. A maioria dos usuários que descobre o produto no início
      do trial assina nos primeiros 14 dias. Os que deixam para o fim perdem
      editais compatíveis que abriram e fecharam enquanto decidiam.
    </p>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 24px;">
      <strong>O que acontece quando você roda a primeira busca:</strong> o
      sistema filtra automaticamente os editais do seu setor e mostra score
      de viabilidade de 0 a 100 para cada um — com peso explicado pelos 4
      fatores (modalidade, prazo, valor, geografia).
    </p>

    <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: 0 auto 24px;">
      <tr>
        <td align="center" style="background: {SMARTLIC_GREEN}; border-radius: 8px;">
          <a href="{FRONTEND_URL}/buscar"
             style="display: inline-block; padding: 14px 28px; color: #fff;
                    text-decoration: none; font-weight: 600; font-size: 16px;">
            Rodar minha primeira busca →
          </a>
        </td>
      </tr>
    </table>

    <p style="color: #888; font-size: 13px; line-height: 1.5; margin: 24px 0 0;">
      Leva 30 segundos: escolhe setor, escolhe UF, clica em buscar. O sistema
      devolve a lista priorizada por score de viabilidade. Sem configuração.
    </p>
    """
    return email_base(
        title="Sua primeira análise está a 30 segundos",
        body_html=body,
        unsubscribe_url=unsubscribe_url,
        is_transactional=False,
    )
