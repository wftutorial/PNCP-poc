"""
STORY-266 AC1-AC4 + STORY-310 AC6-AC8 + STORY-319: Trial email templates.

8 emails in the 14-day trial conversion sequence (STORY-319):
- Day 0:  Welcome — onboarding CTA
- Day 3:  Engagement Early — celebrate usage, show value discovered
- Day 5:  Engagement — deeper feature education
- Day 7:  Tips — midpoint, advanced tips + sector insights
- Day 10: Urgency Light — 4 days remaining, soft CTA
- Day 11: Expiring — 3 days remaining, moderate urgency
- Day 13: Last day — maximum urgency, tomorrow access expires
- Day 16: Expired — reengagement, data saved for 30 days
"""

from templates.emails.base import email_base, SMARTLIC_GREEN, FRONTEND_URL


def _format_brl(value: float) -> str:
    """Format a float as Brazilian Real currency string."""
    if value >= 1_000_000:
        return f"R$ {value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"R$ {value / 1_000:.0f}k"
    return f"R$ {value:,.0f}".replace(",", ".")


def _stats_block(stats: dict, show_pipeline: bool = False) -> str:
    """Render a stats summary block for email templates."""
    searches = stats.get("searches_count", 0)
    opps = stats.get("opportunities_found", 0)
    value = stats.get("total_value_estimated", 0.0)
    pipeline = stats.get("pipeline_items_count", 0)

    rows = f"""
    <tr>
      <td style="padding: 8px 16px; color: #555; font-size: 15px; border-bottom: 1px solid #eee;">
        Buscas realizadas
      </td>
      <td style="padding: 8px 16px; color: #333; font-size: 15px; font-weight: 600; text-align: right; border-bottom: 1px solid #eee;">
        {searches}
      </td>
    </tr>
    <tr>
      <td style="padding: 8px 16px; color: #555; font-size: 15px; border-bottom: 1px solid #eee;">
        Oportunidades encontradas
      </td>
      <td style="padding: 8px 16px; color: #333; font-size: 15px; font-weight: 600; text-align: right; border-bottom: 1px solid #eee;">
        {opps}
      </td>
    </tr>
    <tr>
      <td style="padding: 8px 16px; color: #555; font-size: 15px; border-bottom: 1px solid #eee;">
        Valor total estimado
      </td>
      <td style="padding: 8px 16px; color: {SMARTLIC_GREEN}; font-size: 15px; font-weight: 600; text-align: right; border-bottom: 1px solid #eee;">
        {_format_brl(value)}
      </td>
    </tr>"""

    if show_pipeline:
        rows += f"""
    <tr>
      <td style="padding: 8px 16px; color: #555; font-size: 15px;">
        Itens no pipeline
      </td>
      <td style="padding: 8px 16px; color: #333; font-size: 15px; font-weight: 600; text-align: right;">
        {pipeline}
      </td>
    </tr>"""

    return f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
           style="background-color: #f8f9fa; border-radius: 8px; margin: 16px 0 24px; overflow: hidden;">
      {rows}
    </table>"""


def _unsubscribe_block(unsubscribe_url: str) -> str:
    """Render unsubscribe link block (AC2: RFC 8058 one-click)."""
    if not unsubscribe_url:
        return ""
    return f"""
    <p style="color: #999; font-size: 12px; text-align: center; margin: 24px 0 0;">
      <a href="{unsubscribe_url}" style="color: #999; text-decoration: underline;">
        Não desejo receber emails sobre o trial
      </a>
    </p>"""


# ============================================================================
# Email #1 — Day 0: Welcome (STORY-310 AC6)
# ============================================================================

def render_trial_welcome_email(user_name: str, unsubscribe_url: str = "") -> str:
    """STORY-310 AC6: Day 0 — Welcome email. Onboarding CTA.

    Args:
        user_name: User's display name.
        unsubscribe_url: URL for one-click unsubscribe.
    """
    body = f"""
    <h1 style="color: #333; font-size: 22px; margin: 0 0 16px;">
      Bem-vindo ao SmartLic, {user_name}!
    </h1>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      Seu trial de 14 dias começou. Agora você tem acesso completo à
      plataforma de inteligência em licitações mais avançada do Brasil.
    </p>

    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 24px;">
      <tr>
        <td style="background-color: #e8f5e9; border-radius: 8px; padding: 16px; border-left: 4px solid {SMARTLIC_GREEN};">
          <p style="color: #1b5e20; font-size: 14px; margin: 0; font-weight: 600;">
            O que você pode fazer agora:
          </p>
          <ul style="color: #555; font-size: 14px; margin: 8px 0 0; padding-left: 20px;">
            <li>Buscar licitações por setor e UF com IA</li>
            <li>Analisar viabilidade de cada oportunidade</li>
            <li>Exportar relatórios Excel estilizados</li>
            <li>Montar seu pipeline de oportunidades</li>
          </ul>
        </td>
      </tr>
    </table>

    <p style="text-align: center; margin: 24px 0 16px;">
      <a href="{FRONTEND_URL}/buscar" class="btn"
         style="display: inline-block; padding: 14px 32px; background-color: {SMARTLIC_GREEN}; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
        Fazer minha primeira busca
      </a>
    </p>
    <p style="color: #888; font-size: 13px; text-align: center; margin: 16px 0 0;">
      Seu trial gratuito de 14 dias começou hoje.
    </p>
    {_unsubscribe_block(unsubscribe_url)}
    """

    return email_base(
        title="Bem-vindo ao SmartLic!",
        body_html=body,
        is_transactional=False,
        unsubscribe_url=unsubscribe_url,
    )


# ============================================================================
# Email #2 — Day 3: Engagement Early (existing midpoint, updated copy)
# ============================================================================

def render_trial_midpoint_email(user_name: str, stats: dict, unsubscribe_url: str = "") -> str:
    """Day 3 — engagement early. Celebrate usage, show value.

    Args:
        user_name: User's display name.
        stats: Dict with keys from TrialUsageStats.
        unsubscribe_url: URL for one-click unsubscribe.
    """
    has_usage = stats.get("searches_count", 0) > 0

    if has_usage:
        headline = f"Você já analisou {_format_brl(stats.get('total_value_estimated', 0))} em oportunidades"
        intro = (
            f"Olá, {user_name}! Em apenas 3 dias no SmartLic, você já está "
            f"descobrindo oportunidades reais de licitação."
        )
    else:
        headline = "Você ainda tem 11 dias para descobrir oportunidades"
        intro = (
            f"Olá, {user_name}! Seu trial do SmartLic está apenas começando e "
            f"há oportunidades esperando por você. Faça sua primeira busca agora!"
        )

    body = f"""
    <h1 style="color: #333; font-size: 22px; margin: 0 0 16px;">
      {headline}
    </h1>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      {intro}
    </p>
    {_stats_block(stats) if has_usage else ''}
    <p style="text-align: center; margin: 24px 0 16px;">
      <a href="{FRONTEND_URL}/buscar" class="btn"
         style="display: inline-block; padding: 14px 32px; background-color: {SMARTLIC_GREEN}; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
        Continuar descobrindo oportunidades
      </a>
    </p>
    <p style="color: #888; font-size: 13px; text-align: center; margin: 16px 0 0;">
      Seu trial gratuito termina em 11 dias.
    </p>
    {_unsubscribe_block(unsubscribe_url)}
    """

    return email_base(
        title="Suas primeiras descobertas — SmartLic",
        body_html=body,
        is_transactional=False,
        unsubscribe_url=unsubscribe_url,
    )


# ============================================================================
# Email #3 — Day 7: Engagement (STORY-310 AC6)
# ============================================================================

def render_trial_engagement_email(user_name: str, stats: dict, unsubscribe_url: str = "") -> str:
    """STORY-310 AC6: Day 7 — engagement email. Feature education.

    Args:
        user_name: User's display name.
        stats: Dict with keys from TrialUsageStats.
        unsubscribe_url: URL for one-click unsubscribe.
    """
    has_usage = stats.get("searches_count", 0) > 0
    opps = stats.get("opportunities_found", 0)

    if has_usage and opps > 0:
        headline = f"Você encontrou {opps} oportunidades — descubra como ir além"
    else:
        headline = "Descubra o poder completo do SmartLic"

    body = f"""
    <h1 style="color: #333; font-size: 22px; margin: 0 0 16px;">
      {headline}
    </h1>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      Olá, {user_name}! Sua primeira semana no SmartLic passou rápido.
      Você está aproveitando todos os recursos disponíveis?
    </p>
    {_stats_block(stats, show_pipeline=True) if has_usage else ''}

    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 24px;">
      <tr>
        <td style="background-color: #e3f2fd; border-radius: 8px; padding: 16px; border-left: 4px solid #1976D2;">
          <p style="color: #0d47a1; font-size: 14px; margin: 0; font-weight: 600;">
            Recursos que você pode não ter explorado:
          </p>
          <ul style="color: #555; font-size: 14px; margin: 8px 0 0; padding-left: 20px;">
            <li><strong>Pipeline:</strong> Organize oportunidades em etapas (Kanban)</li>
            <li><strong>Filtros avançados:</strong> UF, modalidade, valor estimado</li>
            <li><strong>Relatório Excel:</strong> Exporte dados estilizados para sua equipe</li>
            <li><strong>Análise IA:</strong> Classificação setorial automática</li>
          </ul>
        </td>
      </tr>
    </table>

    <p style="text-align: center; margin: 24px 0 16px;">
      <a href="{FRONTEND_URL}/buscar" class="btn"
         style="display: inline-block; padding: 14px 32px; background-color: {SMARTLIC_GREEN}; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
        Explorar mais funcionalidades
      </a>
    </p>
    <p style="color: #888; font-size: 13px; text-align: center; margin: 16px 0 0;">
      Seu trial gratuito termina em 9 dias.
    </p>
    {_unsubscribe_block(unsubscribe_url)}
    """

    return email_base(
        title="Descubra mais do SmartLic — Semana 1",
        body_html=body,
        is_transactional=False,
        unsubscribe_url=unsubscribe_url,
    )


# ============================================================================
# Email #4 — Day 14: Tips (STORY-310 AC6)
# ============================================================================

def render_trial_tips_email(user_name: str, stats: dict, unsubscribe_url: str = "") -> str:
    """STORY-310 AC6: Day 14 — tips email. Advanced tips + sector insights.

    Args:
        user_name: User's display name.
        stats: Dict with keys from TrialUsageStats.
        unsubscribe_url: URL for one-click unsubscribe.
    """
    has_usage = stats.get("searches_count", 0) > 0
    value = stats.get("total_value_estimated", 0.0)
    sectors = stats.get("sectors_searched", [])

    if has_usage and value > 0:
        headline = f"Metade do trial: {_format_brl(value)} em oportunidades analisadas"
    else:
        headline = "Metade do trial — dicas para maximizar suas descobertas"

    sectors_tip = ""
    if sectors and len(sectors) > 0:
        sector_names = ", ".join(sectors[:3])
        sectors_tip = f"""
        <li><strong>Amplie setores:</strong> Você buscou em {sector_names}.
          Experimente setores relacionados para mais oportunidades.</li>"""

    body = f"""
    <h1 style="color: #333; font-size: 22px; margin: 0 0 16px;">
      {headline}
    </h1>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      Olá, {user_name}! Você está na metade do seu trial de 14 dias.
      Aqui vão algumas dicas para encontrar ainda mais oportunidades relevantes:
    </p>
    {_stats_block(stats, show_pipeline=True) if has_usage else ''}

    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 24px;">
      <tr>
        <td style="background-color: #fff8e1; border-radius: 8px; padding: 16px; border-left: 4px solid #f9a825;">
          <p style="color: #e65100; font-size: 14px; margin: 0; font-weight: 600;">
            Dicas de especialista:
          </p>
          <ul style="color: #555; font-size: 14px; margin: 8px 0 0; padding-left: 20px;">
            <li><strong>Busca multi-UF:</strong> Selecione vários estados para ampliar resultados</li>
            {sectors_tip}
            <li><strong>Pipeline:</strong> Arraste oportunidades para acompanhar prazos</li>
            <li><strong>Alertas:</strong> Configure alertas para não perder novas licitações</li>
          </ul>
        </td>
      </tr>
    </table>

    <p style="text-align: center; margin: 24px 0 16px;">
      <a href="{FRONTEND_URL}/buscar" class="btn"
         style="display: inline-block; padding: 14px 32px; background-color: {SMARTLIC_GREEN}; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
        Aplicar essas dicas agora
      </a>
    </p>
    <p style="color: #888; font-size: 13px; text-align: center; margin: 16px 0 0;">
      Seu trial gratuito termina em 7 dias.
    </p>
    {_unsubscribe_block(unsubscribe_url)}
    """

    return email_base(
        title="Dicas para maximizar seu trial — SmartLic",
        body_html=body,
        is_transactional=False,
        unsubscribe_url=unsubscribe_url,
    )


# ============================================================================
# Email #5 — Day 21: Urgency Light (STORY-310 AC6)
# ============================================================================

def render_trial_urgency_email(user_name: str, stats: dict, days_remaining: int = 4, unsubscribe_url: str = "") -> str:
    """STORY-319: Day 10 — urgency light. Soft CTA to upgrade.

    Args:
        user_name: User's display name.
        stats: Dict with keys from TrialUsageStats.
        days_remaining: Days left in trial (typically 4 for 14-day trial).
        unsubscribe_url: URL for one-click unsubscribe.
    """
    value = stats.get("total_value_estimated", 0.0)
    opps = stats.get("opportunities_found", 0)

    if value > 0:
        headline = f"Restam {days_remaining} dias — você já descobriu {_format_brl(value)} em oportunidades"
    elif opps > 0:
        headline = f"Restam {days_remaining} dias — {opps} oportunidades encontradas"
    else:
        headline = f"Restam {days_remaining} dias no seu trial SmartLic"

    body = f"""
    <h1 style="color: #333; font-size: 22px; margin: 0 0 16px;">
      {headline}
    </h1>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      Olá, {user_name}! Seu trial do SmartLic termina em {days_remaining} dias.
      Garanta que você não perca acesso às oportunidades que está acompanhando.
    </p>
    {_stats_block(stats, show_pipeline=True)}
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 24px;">
      Com o SmartLic Pro, você mantém acesso a buscas ilimitadas, IA de classificação,
      relatórios e pipeline — sem interrupção.
    </p>
    <p style="text-align: center; margin: 24px 0 16px;">
      <a href="{FRONTEND_URL}/planos" class="btn"
         style="display: inline-block; padding: 14px 32px; background-color: {SMARTLIC_GREEN}; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
        Conhecer o SmartLic Pro
      </a>
    </p>
    <p style="color: #888; font-size: 13px; text-align: center; margin: 16px 0 0;">
      Economize 20% com o plano anual.
    </p>
    {_unsubscribe_block(unsubscribe_url)}
    """

    return email_base(
        title=f"Restam {days_remaining} dias de trial — SmartLic",
        body_html=body,
        is_transactional=False,
        unsubscribe_url=unsubscribe_url,
    )


# ============================================================================
# Email #6 — Day 11: Expiring (STORY-319: updated for 14-day trial)
# ============================================================================

def render_trial_expiring_email(user_name: str, days_remaining: int, stats: dict, unsubscribe_url: str = "") -> str:
    """Day 11 — 3 days remaining. Informative with moderate urgency.

    Args:
        user_name: User's display name.
        days_remaining: Days left in trial (typically 3 for 14-day trial).
        stats: Dict with keys from TrialUsageStats.
        unsubscribe_url: URL for one-click unsubscribe.
    """
    body = f"""
    <h1 style="color: #333; font-size: 22px; margin: 0 0 16px;">
      Seu acesso completo ao SmartLic acaba em {days_remaining} dias
    </h1>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      Olá, {user_name}! Seu período de trial está chegando ao fim.
      Veja o que você já conquistou:
    </p>
    {_stats_block(stats, show_pipeline=True)}
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 24px;">
      Para continuar tendo acesso completo a buscas ilimitadas, análise por IA,
      relatórios Excel e pipeline de oportunidades, ative o SmartLic Pro.
    </p>
    <p style="text-align: center; margin: 24px 0 16px;">
      <a href="{FRONTEND_URL}/planos" class="btn"
         style="display: inline-block; padding: 14px 32px; background-color: {SMARTLIC_GREEN}; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
        Garantir acesso contínuo
      </a>
    </p>
    {_unsubscribe_block(unsubscribe_url)}
    """

    return email_base(
        title="Seu trial expira em breve — SmartLic",
        body_html=body,
        is_transactional=False,
        unsubscribe_url=unsubscribe_url,
    )


# ============================================================================
# Email #7 — Day 13: Last Day (STORY-319: updated for 14-day trial)
# ============================================================================

def render_trial_last_day_email(user_name: str, stats: dict, unsubscribe_url: str = "") -> str:
    """Day 13 — last day. Maximum urgency.

    Args:
        user_name: User's display name.
        stats: Dict with keys from TrialUsageStats.
        unsubscribe_url: URL for one-click unsubscribe.
    """
    body = f"""
    <h1 style="color: #d32f2f; font-size: 22px; margin: 0 0 16px;">
      Amanhã seu acesso expira — não perca o que você construiu
    </h1>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      Olá, {user_name}! Este é o <strong>último dia</strong> do seu trial no SmartLic.
      Amanhã você perderá acesso às funcionalidades completas.
    </p>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 8px;">
      <strong>Resumo do seu trial:</strong>
    </p>
    {_stats_block(stats, show_pipeline=True)}

    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 24px;">
      <tr>
        <td style="background-color: #fff3e0; border-radius: 8px; padding: 16px; border-left: 4px solid #ff9800;">
          <p style="color: #e65100; font-size: 14px; margin: 0; font-weight: 600;">
            Ative hoje e não perca nenhuma oportunidade
          </p>
          <p style="color: #555; font-size: 14px; margin: 8px 0 0;">
            SmartLic Pro — R$ 397/mês &nbsp;|&nbsp;
            Economia de 20% no plano anual
          </p>
        </td>
      </tr>
    </table>

    <p style="text-align: center; margin: 24px 0 16px;">
      <a href="{FRONTEND_URL}/planos" class="btn"
         style="display: inline-block; padding: 14px 32px; background-color: #d32f2f; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
        Ativar SmartLic Pro — R$ 397/mês
      </a>
    </p>
    {_unsubscribe_block(unsubscribe_url)}
    """

    return email_base(
        title="Último dia de trial — SmartLic",
        body_html=body,
        is_transactional=False,
        unsubscribe_url=unsubscribe_url,
    )


# ============================================================================
# Email #8 — Day 16: Expired (STORY-319: updated for 14-day trial)
# ============================================================================

def render_trial_expired_email(user_name: str, stats: dict, unsubscribe_url: str = "") -> str:
    """Day 16 — 2 days after expiry. Reengagement.

    Args:
        user_name: User's display name.
        stats: Dict with keys from TrialUsageStats.
        unsubscribe_url: URL for one-click unsubscribe.
    """
    opps = stats.get("opportunities_found", 0)
    pipeline = stats.get("pipeline_items_count", 0)

    # Adapt headline based on usage
    if opps > 0 or pipeline > 0:
        if pipeline > 0:
            headline = f"Suas {pipeline} oportunidades estão esperando por você"
        else:
            headline = f"Suas {opps} oportunidades estão esperando por você"
    else:
        headline = "As oportunidades de licitação continuam surgindo"

    body = f"""
    <h1 style="color: #333; font-size: 22px; margin: 0 0 16px;">
      {headline}
    </h1>
    <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 16px;">
      Olá, {user_name}! Seu trial expirou, mas seus dados ficam salvos por 30 dias.
      Reative o acesso para continuar de onde parou.
    </p>
    {_stats_block(stats, show_pipeline=True) if (opps > 0 or pipeline > 0) else ''}
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 0 0 24px;">
      <tr>
        <td style="background-color: #e8f5e9; border-radius: 8px; padding: 16px; border-left: 4px solid {SMARTLIC_GREEN};">
          <p style="color: #1b5e20; font-size: 14px; margin: 0;">
            Seus dados ficam salvos por 30 dias — buscas, pipeline e histórico.
          </p>
        </td>
      </tr>
    </table>

    <p style="text-align: center; margin: 24px 0 16px;">
      <a href="{FRONTEND_URL}/planos" class="btn"
         style="display: inline-block; padding: 14px 32px; background-color: {SMARTLIC_GREEN}; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
        Reativar acesso
      </a>
    </p>
    {_unsubscribe_block(unsubscribe_url)}
    """

    return email_base(
        title="Seu trial expirou — SmartLic",
        body_html=body,
        is_transactional=False,
        unsubscribe_url=unsubscribe_url,
    )
