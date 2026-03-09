# CROSS-006: Staging Environment Setup

## Status: Pendente Configuracao Externa

## Objetivo
Criar ambiente de staging isolado para testes E2E e validacao pre-deploy, eliminando uso de producao para testes.

## Arquitetura

```
Production                          Staging
┌──────────────┐                   ┌──────────────┐
│ Railway      │                   │ Railway      │
│ - web        │                   │ - web-stg    │
│ - worker     │                   │ - worker-stg │
│ - frontend   │                   │ - frontend-stg│
└──────┬───────┘                   └──────┬───────┘
       │                                  │
┌──────┴───────┐                   ┌──────┴───────┐
│ Supabase     │                   │ Supabase     │
│ (prod)       │                   │ (staging)    │
│ fqqyovlzdz.. │                   │ <new-ref>    │
└──────────────┘                   └──────────────┘
```

## Passos de Implementacao

### 1. Supabase Staging Project

```bash
# Criar novo projeto Supabase
npx supabase projects create smartlic-staging --org-id <org-id> --region sa-east-1

# Linkar e aplicar migracoes
npx supabase link --project-ref <staging-ref>
npx supabase db push --include-all

# Seed com dados de teste (nao dados reais)
npx supabase db seed
```

### 2. Railway Staging Services

```bash
# Criar servicos staging no Railway
railway service create web-staging
railway service create worker-staging
railway service create frontend-staging

# Configurar variaveis (copiar de prod, alterar URLs)
railway variables set SUPABASE_URL=https://<staging-ref>.supabase.co
railway variables set SUPABASE_ANON_KEY=<staging-anon-key>
railway variables set SUPABASE_SERVICE_ROLE_KEY=<staging-service-key>
railway variables set NEXT_PUBLIC_ENVIRONMENT=staging
railway variables set LOG_LEVEL=DEBUG
```

### 3. Dominio Staging

```
staging.smartlic.tech -> frontend-staging.railway.app
api-staging.smartlic.tech -> web-staging.railway.app
```

### 4. CI/CD Staging Deploy

Adicionar ao `.github/workflows/deploy.yml`:

```yaml
staging-deploy:
  if: github.ref == 'refs/heads/develop' || github.event_name == 'workflow_dispatch'
  environment: staging
  steps:
    - uses: actions/checkout@v4
    - name: Deploy to Railway staging
      run: railway up --service web-staging
      env:
        RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN_STAGING }}
```

### 5. E2E no Staging (SYS-033)

Atualizar `frontend/e2e-tests/`:

```typescript
// playwright.config.ts
const baseURL = process.env.STAGING_URL || 'https://staging.smartlic.tech';
```

Criar usuarios de teste no Supabase staging (nao usar credenciais de producao).

### 6. Checklist de Validacao

- [ ] Supabase staging project criado com todas migracoes
- [ ] Railway staging services rodando
- [ ] DNS staging configurado
- [ ] CI/CD deployando para staging no push para develop
- [ ] E2E tests rodando contra staging
- [ ] Dados de teste seedados (nao dados reais)
- [ ] Feature flags independentes de producao

### Custos Estimados
- Supabase Free Tier: $0 (suficiente para staging)
- Railway: ~$5-10/mo (trial credits ou Hobby plan)
- Total: $0-10/mo
