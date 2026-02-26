# STORY-288: Social Proof Autentico — Testimonials Reais & Logo Bar

**Priority:** P1 (Pre-Paid Acquisition)
**Effort:** M (3-5 days — depende de outreach para beta users)
**Squad:** @pm + @ux-design-expert
**Fundamentacao:** GTM Readiness Audit Track 8 (Market) — MKT-013, MKT-014
**Status:** TODO
**Sprint:** GTM Sprint 2 (Pre-Acquisition)

---

## Contexto

O audit de GTM identificou que os testimonials atuais sao "PO-curated, representative of real usage patterns" — ou seja, construidos/representativos e nao de usuarios reais. Para B2B SaaS no mercado de licitacoes, social proof autentico com identidade verificavel e critico para conversao.

Alem disso, nao ha logo bar de empresas na landing page — um dos elementos de social proof mais impactantes para B2B.

---

## Acceptance Criteria

### AC1: Coletar testimonials reais
- [ ] Identificar 5-8 beta users mais ativos (via analytics/searches)
- [ ] Enviar email de outreach pedindo testimonial + permissao de uso
- [ ] Template de outreach: nome, empresa, setor, quote, nota (1-5 estrelas)
- [ ] Oferecer incentivo: 1 mes gratis de SmartLic Pro
- [ ] Minimo 3 testimonials reais coletados

### AC2: Atualizar TestimonialSection com dados reais
- [ ] Substituir testimonials construidos por reais em `frontend/components/TestimonialSection.tsx`
- [ ] Incluir: nome completo, cargo, empresa real, setor, foto (se autorizado)
- [ ] Manter fallback para testimonials representativos se <3 reais coletados
- [ ] Adicionar badge "Beta user verificado" em cada testimonial

### AC3: Adicionar logo bar na landing page
- [ ] Coletar logos das empresas beta (com autorizacao)
- [ ] Criar componente `LogoBar.tsx` ou `TrustedBy.tsx`
- [ ] Posicionar abaixo do HeroSection ou acima dos testimonials
- [ ] Heading: "Empresas que ja usam o SmartLic"
- [ ] Minimo 3 logos, maximo 8
- [ ] Versoes grayscale com hover colorido

### AC4: Adicionar estatisticas agregadas
- [ ] Calcular e exibir metricas reais:
  - Total de oportunidades analisadas
  - Total de valor em editais processados
  - Numero de setores cobertos (15)
  - Numero de UFs cobertas (27)
- [ ] Componente `PlatformStats` ou similar na landing page
- [ ] Dados podem ser hardcoded inicialmente, depois dinamicos via API

---

## Arquivos Impactados

| Arquivo | Mudanca |
|---------|---------|
| `frontend/components/TestimonialSection.tsx` | Dados reais |
| `frontend/app/components/LogoBar.tsx` | NOVO — logo bar |
| `frontend/app/page.tsx` | Adicionar LogoBar + PlatformStats |
| Email outreach template | NOVO |
