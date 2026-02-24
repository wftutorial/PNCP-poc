# UX-358 — Menu Mobile da Landing Trava Navegacao e Impede Retorno

**Status:** Ready
**Priority:** P1 — Critical (bloqueio de conversao)
**Severity:** Funcional — impede uso completo no mobile
**Created:** 2026-02-24
**Sprint:** Next
**Relates to:** UX-340 (MobileDrawer autenticado)

---

## Problema

No mobile, o menu hamburger da landing page (`/`) tem experiencia terrivel:

1. **Header translucido obstrui conteudo** — Quando o usuario rola a pagina, o header muda para `bg-surface-0/70 backdrop-blur-xl` (70% opacidade), criando um efeito translucido que compete visualmente com o conteudo da pagina, especialmente em dispositivos com telas menores.

2. **Menu trava a pagina** — Ao abrir o menu, `document.body.style.overflow = 'hidden'` e aplicado (MobileMenu.tsx:31). Se o menu nao fechar corretamente (edge cases de navegacao, touch events perdidos, ou back button do browser), o `overflow: hidden` persiste e **toda a pagina fica travada** sem scroll.

3. **Impossivel retornar a tela inicial** — O menu nao tem mecanismo de fallback robusto para destravar a pagina. O botao de voltar do browser nao fecha o menu (nao usa History API). Nao ha timeout de seguranca. Se o overlay click falhar, o usuario fica preso.

4. **Overlay translucido confuso** — O overlay usa `bg-black/50 backdrop-blur-sm` (MobileMenu.tsx:63) que, combinado com o header translucido, cria uma camada visual confusa onde o usuario nao sabe exatamente onde clicar para fechar.

### Impacto

- **Bloqueio total de conversao mobile** — usuario nao consegue navegar, cadastrar-se, ou fazer login
- Mobile representa ~60% do trafego de landing pages B2G
- Qualquer falha no close handler = pagina permanentemente travada ate F5

### Causa Raiz

Arquivos envolvidos:
- `frontend/components/layout/MobileMenu.tsx` — scroll lock via `document.body.style.overflow`
- `frontend/app/components/landing/LandingNavbar.tsx` — estado `isMobileMenuOpen` + header translucido

O componente depende de 4 mecanismos de close (overlay click, botao X, Escape, link click) mas nao tem **nenhum fallback** se todos falharem. Alem disso, nao integra com a History API do browser (back button).

---

## Acceptance Criteria

### AC1 — Header opaco no mobile (remover translucidez problematica)
- [ ] No mobile (<768px), quando scrollado, header usa background **100% opaco** (`bg-[var(--surface-0)]` sem opacity)
- [ ] Desktop mantem o efeito translucido atual (nao regredir)
- [ ] Transicao de transparente para opaco mantem-se suave (300ms)

### AC2 — Body scroll lock robusto com failsafe
- [ ] Substituir `document.body.style.overflow = 'hidden'` por abordagem mais robusta:
  - Usar `position: fixed` + `top: -scrollY` + restaurar scroll position no close
  - OU usar `overscroll-behavior: contain` no painel do menu
- [ ] Adicionar **timeout de seguranca** (10s): se menu estiver aberto por >10s sem interacao, log warning
- [ ] Cleanup no `useEffect` return garante 100% que overflow e restaurado em **qualquer** cenario de unmount

### AC3 — Integracao com History API (back button fecha menu)
- [ ] Ao abrir o menu, fazer `window.history.pushState({ mobileMenu: true }, '')`
- [ ] Listener `popstate` fecha o menu quando usuario pressiona back button
- [ ] Impedir que back button navegue para pagina anterior enquanto menu esta aberto
- [ ] Cleanup do listener no unmount

### AC4 — Overlay com area de toque clara
- [ ] Overlay muda de `bg-black/50 backdrop-blur-sm` para `bg-black/60` (sem blur, mais opaco)
- [ ] Area de toque do overlay deve cobrir 100% da tela excluindo o painel do menu
- [ ] Tap/click no overlay fecha menu de forma confiavel (testar com touch events reais)

### AC5 — Botao de fechar acessivel e visivel
- [ ] Botao X no menu tem `min-h-[48px] min-w-[48px]` (aumentar de 44px para melhor touch)
- [ ] Adicionar label textual "Fechar" ao lado do X para clareza
- [ ] Focus trap dentro do menu enquanto aberto (Tab nao sai do painel)

### AC6 — Fallback de emergencia
- [ ] Se `overflow: hidden` persistir no body apos menu fechar, remover automaticamente em 500ms (MutationObserver ou requestAnimationFrame check)
- [ ] Adicionar `data-mobile-menu-open` attribute no body para debugging
- [ ] Console.warn se scroll lock durar >15 segundos

### AC7 — Testes
- [ ] Atualizar testes existentes em `frontend/__tests__/layout/mobile-menu.test.tsx` (18 testes)
- [ ] Adicionar teste: back button fecha menu
- [ ] Adicionar teste: scroll lock removido no unmount inesperado
- [ ] Adicionar teste: timeout de seguranca emite warning
- [ ] Adicionar teste: overlay sem backdrop-blur
- [ ] Todos os 18+ testes existentes continuam passando

---

## Solucao Tecnica Proposta

### 1. Header opaco no mobile

```tsx
// LandingNavbar.tsx — linha 35-39
<header className={`sticky top-0 z-50 transition-all duration-300 ${
  isScrolled
    ? 'bg-[var(--surface-0)] md:bg-surface-0/70 md:backdrop-blur-xl shadow-[0_1px_3px_rgba(0,0,0,0.04)] border-b border-[var(--border)]/50'
    : 'bg-transparent'
} ${className}`}>
```

### 2. Scroll lock robusto

```tsx
// MobileMenu.tsx — substituir linhas 28-38
useEffect(() => {
  if (isOpen) {
    const scrollY = window.scrollY;
    document.body.style.position = 'fixed';
    document.body.style.top = `-${scrollY}px`;
    document.body.style.width = '100%';
    document.body.setAttribute('data-mobile-menu-open', 'true');
  } else {
    const scrollY = document.body.style.top;
    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.width = '';
    document.body.removeAttribute('data-mobile-menu-open');
    window.scrollTo(0, parseInt(scrollY || '0') * -1);
  }
  return () => {
    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.width = '';
    document.body.removeAttribute('data-mobile-menu-open');
  };
}, [isOpen]);
```

### 3. History API integration

```tsx
useEffect(() => {
  if (!isOpen) return;
  window.history.pushState({ mobileMenu: true }, '');
  const handlePopState = (e: PopStateEvent) => {
    onClose();
  };
  window.addEventListener('popstate', handlePopState);
  return () => window.removeEventListener('popstate', handlePopState);
}, [isOpen, onClose]);
```

---

## Arquivos a Modificar

| Arquivo | Mudanca |
|---------|---------|
| `frontend/components/layout/MobileMenu.tsx` | Scroll lock robusto, History API, overlay, failsafe |
| `frontend/app/components/landing/LandingNavbar.tsx` | Header opaco no mobile |
| `frontend/__tests__/layout/mobile-menu.test.tsx` | Novos testes + atualizacao dos existentes |

---

## Validacao

- [ ] Testar em iPhone SE (320px) — menor viewport
- [ ] Testar em iPhone 13/14 (390px) — mais comum
- [ ] Testar em Android (360px) — variante comum
- [ ] Abrir menu > pressionar back > menu fecha, pagina nao navega
- [ ] Abrir menu > esperar 15s > verificar console warning
- [ ] Abrir menu > forcar unmount do componente > body volta ao normal
- [ ] Navegar landing inteira sem nenhum travamento

## Definition of Done

- [ ] Todos os AC passando
- [ ] 0 falhas nos testes existentes (18 base + novos)
- [ ] Testado manualmente em 3 viewports mobile
- [ ] Sem regressao no desktop
- [ ] Code review aprovado
