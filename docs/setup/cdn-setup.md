# SYS-019: CDN Setup para Assets Estaticos

## Status: Pendente Configuracao Externa

## Objetivo
Servir assets estaticos (JS, CSS, imagens, fontes) via CDN ao inves de diretamente do Railway, reduzindo latencia e carga no servidor.

## Opcao Recomendada: Cloudflare (Free Tier)

### Passos de Implementacao

1. **Criar conta Cloudflare** (se nao existir)
   - Acessar https://dash.cloudflare.com/sign-up

2. **Adicionar dominio smartlic.tech**
   - Dashboard > Add a Site > smartlic.tech
   - Selecionar plano Free
   - Atualizar nameservers no registrador

3. **Configurar DNS**
   ```
   A     smartlic.tech       -> Railway IP (proxy mode ON - laranja)
   CNAME www                 -> smartlic.tech (proxy mode ON)
   CNAME api                 -> backend.railway.app (proxy mode ON)
   ```

4. **Configurar Cache Rules**
   ```
   # Cache static assets por 30 dias
   /_next/static/*  -> Cache: 30d, Browser TTL: 30d
   /images/*        -> Cache: 7d, Browser TTL: 7d
   /fonts/*         -> Cache: 365d, Browser TTL: 365d

   # Bypass cache para API e paginas dinamicas
   /api/*           -> Cache: Bypass
   /buscar*         -> Cache: Bypass
   /dashboard*      -> Cache: Bypass
   ```

5. **Configurar Page Rules (Free: 3 regras)**
   - `smartlic.tech/_next/static/*` -> Cache Everything, Edge TTL: 1 month
   - `smartlic.tech/api/*` -> Cache Bypass
   - `smartlic.tech/*.html` -> Cache Standard

6. **Headers de Cache no Next.js** (`next.config.js`)
   ```javascript
   async headers() {
     return [
       {
         source: '/_next/static/:path*',
         headers: [
           { key: 'Cache-Control', value: 'public, max-age=2592000, immutable' },
         ],
       },
       {
         source: '/images/:path*',
         headers: [
           { key: 'Cache-Control', value: 'public, max-age=604800' },
         ],
       },
     ];
   }
   ```

7. **Validacao**
   - `curl -I https://smartlic.tech/_next/static/chunks/main.js` -> verificar `cf-cache-status: HIT`
   - Dashboard Cloudflare > Analytics > ver taxa de cache hit

### Beneficios Esperados
- Reducao de ~60% na bandwidth do Railway
- Latencia < 50ms para assets (POPs globais Cloudflare)
- Protecao DDoS automatica (camada 3/4/7)
- SSL automatico e gratuito

### Custo
- Free Tier: suficiente para nosso volume atual
- Pro ($20/mo): considerar se precisar de WAF avancado ou Image Optimization
