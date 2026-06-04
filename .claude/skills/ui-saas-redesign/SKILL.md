---
name: ui-saas-redesign
description: Guidelines for redesigning the app shell from the sticky top nav to a modern SaaS layout with a fixed left sidebar that collapses to an icon rail at 1024px. Use this skill when restructuring the navigation, layout, or app shell in client/src/App.vue.
---

# UI SaaS Redesign: Top Nav to Left Sidebar

Guidelines for converting this app's shell from the sticky top nav bar into a modern SaaS layout: a fixed left vertical sidebar (240px) that collapses to a 64px icon-only rail at 1024px, a slim content topbar for user controls, and consistent spacing via `:root` design tokens.

**MANDATORY:** All `.vue` file creation or modification MUST be delegated to the **vue-expert** subagent when it is available in the session. If vue-expert is unavailable, apply these guidelines directly.

## Overview

```
CURRENT                                TARGET
+--------------------------------+    +-------+------------------------+
| header.top-nav (sticky, 70px)  |    | side  | .content-topbar (56px) |
|  logo | nav-tabs | lang | user |    | bar   +------------------------+
+--------------------------------+    |       | FilterBar (sticky)     |
| FilterBar (sticky, top: 70px)  |    | 240px +------------------------+
+--------------------------------+    | (64px | main.main-content      |
| main.main-content              |    | rail  |   <router-view />      |
|   <router-view />              |    | @1024)|                        |
+--------------------------------+    +-------+------------------------+
```

Out of scope (intentional non-goals): mobile hamburger/overlay. Collapse happens two ways: automatically via the CSS 1024px breakpoint, and manually via a toggle button whose state lives in `client/src/composables/useSidebar.js` (module-level ref persisted to `localStorage['sidebar-collapsed']`, same pattern as `useFilters`). The manual toggle is hidden at <=1024px where the viewport forces the rail. `App.vue` binds `.sidebar-collapsed` on `.app` to shrink the grid column; `AppSidebar.vue` binds `.collapsed` on the aside to hide labels.

## Target Layout Spec

Add design tokens at the top of App.vue's global (unscoped) style block. The codebase currently has zero CSS custom properties and zero media queries; these are new:

```css
:root {
  --sidebar-width: 240px;
  --sidebar-width-collapsed: 64px;
  --topbar-height: 56px;
  --color-text: #0f172a;
  --color-text-muted: #64748b;
  --color-border: #e2e8f0;
  --color-bg: #f8fafc;
  --color-accent: #2563eb;
  --color-accent-bg: #eff6ff;
  --z-sidebar: 100;
  --z-filter-bar: 90;
}

@media (max-width: 1024px) {
  :root {
    --sidebar-width: var(--sidebar-width-collapsed);
  }
}
```

Replace the current shell rules (App.vue `.app` is `flex-direction: column`):

```css
.app {
  display: grid;
  grid-template-columns: var(--sidebar-width) 1fr;
  min-height: 100vh;
}

.content-column {
  display: flex;
  flex-direction: column;
  min-width: 0; /* prevents grid blowout from wide tables */
}

.content-topbar {
  height: var(--topbar-height);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;
  padding: 0 2rem;
  background: white;
  border-bottom: 1px solid var(--color-border);
}
```

`.main-content` keeps `flex: 1; max-width: 1600px; margin: 0 auto; padding: 1.5rem 2rem` unchanged. It now centers within the content column instead of the viewport; at very wide screens content sits ~120px right of true viewport center. This is expected and correct for a sidebar layout. Views need no changes: none of them define their own width or padding.

Use CSS Grid (not `position: fixed` + `margin-left`) so the sidebar and content can never drift out of sync, and window scrolling is preserved so FilterBar's `position: sticky` keeps working with the same mechanism.

## New Component: AppSidebar.vue

Create `client/src/components/AppSidebar.vue`. Icons are inline SVG with `stroke: currentColor` (design system: custom SVG only, no emojis). Active state uses manual `$route.path` comparison, same as the current App.vue nav (the app does not use `router-link-active` classes).

```vue
<template>
  <aside class="sidebar">
    <div class="sidebar-logo">
      <span class="logo-monogram">FI</span>
      <div class="logo-text">
        <h1>{{ t('nav.companyName') }}</h1>
        <span class="subtitle">{{ t('nav.subtitle') }}</span>
      </div>
    </div>
    <nav class="sidebar-nav">
      <router-link to="/" :class="{ active: $route.path === '/' }" :title="t('nav.overview')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
          <rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>
        </svg>
        <span class="nav-label">{{ t('nav.overview') }}</span>
      </router-link>
      <router-link to="/inventory" :class="{ active: $route.path === '/inventory' }" :title="t('nav.inventory')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 8l-9-5-9 5v8l9 5 9-5V8z"/><path d="M3 8l9 5 9-5"/><path d="M12 13v8"/>
        </svg>
        <span class="nav-label">{{ t('nav.inventory') }}</span>
      </router-link>
      <router-link to="/orders" :class="{ active: $route.path === '/orders' }" :title="t('nav.orders')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 3h6a1 1 0 011 1v1h3a1 1 0 011 1v14a1 1 0 01-1 1H5a1 1 0 01-1-1V6a1 1 0 011-1h3V4a1 1 0 011-1z"/>
          <path d="M9 12h6M9 16h4"/>
        </svg>
        <span class="nav-label">{{ t('nav.orders') }}</span>
      </router-link>
      <router-link to="/spending" :class="{ active: $route.path === '/spending' }" :title="t('nav.finance')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="9"/><path d="M14.5 9.5c-.5-1-1.5-1.5-2.5-1.5-1.5 0-2.5 1-2.5 2 0 2.5 5 1.5 5 4 0 1-1 2-2.5 2-1 0-2-.5-2.5-1.5M12 6.5v11"/>
        </svg>
        <span class="nav-label">{{ t('nav.finance') }}</span>
      </router-link>
      <router-link to="/demand" :class="{ active: $route.path === '/demand' }" :title="t('nav.demandForecast')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>
        </svg>
        <span class="nav-label">{{ t('nav.demandForecast') }}</span>
      </router-link>
      <router-link to="/reports" :class="{ active: $route.path === '/reports' }" :title="t('nav.reports')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/><path d="M14 2v6h6"/><path d="M9 13h6M9 17h6"/>
        </svg>
        <span class="nav-label">{{ t('nav.reports') }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script>
import { useI18n } from '../composables/useI18n'

export default {
  name: 'AppSidebar',
  setup() {
    const { t } = useI18n()
    return { t }
  }
}
</script>

<style scoped>
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  background: white;
  border-right: 1px solid var(--color-border);
  z-index: var(--z-sidebar);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 1rem;
  border-bottom: 1px solid var(--color-border);
}

.logo-monogram {
  display: none;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--color-accent);
  color: white;
  font-weight: 700;
  font-size: 0.85rem;
  align-items: center;
  justify-content: center;
}

.logo-text h1 { font-size: 1rem; font-weight: 700; color: var(--color-text); }
.logo-text .subtitle { font-size: 0.75rem; color: var(--color-text-muted); }

.sidebar-nav { display: flex; flex-direction: column; gap: 2px; padding: 0.75rem 0.5rem; }

.sidebar-nav a {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  border-left: 2px solid transparent;
  color: var(--color-text-muted);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
}

.sidebar-nav a:hover { background: var(--color-bg); color: var(--color-text); }

.sidebar-nav a.active {
  background: var(--color-accent-bg);
  color: var(--color-accent);
  border-left-color: var(--color-accent);
}

.nav-icon { width: 18px; height: 18px; flex-shrink: 0; }

@media (max-width: 1024px) {
  .nav-label, .logo-text { display: none; }
  .logo-monogram { display: flex; }
  .sidebar-logo { justify-content: center; padding: 1rem 0.5rem; }
  .sidebar-nav a { justify-content: center; padding: 0.6rem; }
}
</style>
```

## App.vue Restructure

New template skeleton (modals and their wiring stay exactly as they are):

```vue
<template>
  <div class="app">
    <AppSidebar />
    <div class="content-column">
      <header class="content-topbar">
        <LanguageSwitcher />
        <ProfileMenu
          @show-profile-details="..."
          @show-tasks="..."
        />
      </header>
      <FilterBar />
      <main class="main-content">
        <router-view />
      </main>
    </div>
    <!-- ProfileDetailsModal and TasksModal unchanged -->
  </div>
</template>
```

ProfileMenu's `@show-profile-details` / `@show-tasks` event wiring moves verbatim from the old header to the topbar. ProfileMenu and LanguageSwitcher go in the topbar, NOT the sidebar footer: both render absolutely-positioned dropdowns that open downward, and at 64px rail width they would not fit.

**Deletion list** for the global style block — remove these rules entirely (do not leave them orphaned; the `.nav-container > X` child selectors silently stop matching when the markup changes, which hides mistakes):

- `.top-nav`
- `.nav-container`
- `.nav-container > .nav-tabs` and all `.nav-tabs*` rules (including the `.active::after` underline, replaced by the sidebar's left accent border)
- `.nav-container > .language-switcher` (and any other `.nav-container >` rules)
- `.logo` / `.subtitle` rules tied to the old header (the sidebar has its own scoped versions)

**Preserve untouched:** the rest of the global style block — `.page-header`, `.stats-grid`, `.stat-card*`, `.card*`, `.table-container`, table styles, `.badge*`, `.loading`, `.error`. Every view depends on these.

## FilterBar.vue Changes

Exactly two facts, one edit:

1. `.filters-bar` has `position: sticky; top: 70px; z-index: 90` — the `70px` hardcodes the height of the top nav being removed. Change to `top: 0`. The topbar is non-sticky, so FilterBar sticks to the viewport top on scroll.
2. Keep `z-index: 90` and the `.filters-container` max-width/padding as they are.

Spending.vue's sticky `thead` (`top: 0` within its own scroll container) is unaffected.

## i18n

The Reports link is currently hardcoded `"Reports"` with no i18n key. Add `reports` to the `nav` block of BOTH locale files, then use `t('nav.reports')` in the sidebar:

| File | Addition |
|---|---|
| `client/src/locales/en.js` | `reports: 'Reports'` |
| `client/src/locales/ja.js` | `reports: 'レポート'` |

Full nav key reference after the change:

| Key | Route |
|---|---|
| `nav.companyName` | (logo) |
| `nav.subtitle` | (logo) |
| `nav.overview` | `/` |
| `nav.inventory` | `/inventory` |
| `nav.orders` | `/orders` |
| `nav.finance` | `/spending` |
| `nav.demandForecast` | `/demand` |
| `nav.reports` | `/reports` |

## Step-by-Step Procedure

1. Add `nav.reports` to `client/src/locales/en.js` and `ja.js` (plain JS, no vue-expert needed)
2. Create `client/src/components/AppSidebar.vue` — delegate to vue-expert
3. Restructure `App.vue`: new template skeleton, `:root` tokens, shell CSS, deletion list — delegate to vue-expert
4. Update `FilterBar.vue` sticky offset (`top: 70px` → `top: 0`) — delegate to vue-expert
5. Run the verification checklist below

## Z-Index Ladder

| Layer | z-index |
|---|---|
| Modals (ProfileDetails, Tasks, detail modals) | 1000–2000 |
| ProfileMenu / LanguageSwitcher dropdowns | 1000 |
| Sidebar | 100 |
| FilterBar | 90 |
| Spending sticky thead | 1 |

Rule: never raise the sidebar above 100. Dropdowns and modals must always overlay it.

## Verification Checklist

Use Playwright MCP against `http://localhost:3000` (per project CLAUDE.md):

- [ ] All 6 routes render; the matching sidebar link shows the active state on each
- [ ] Sidebar stays fixed while scrolling a long view (Orders or Inventory)
- [ ] FilterBar sticks to the viewport top on scroll, content scrolls beneath it
- [ ] LanguageSwitcher and ProfileMenu dropdowns open from the topbar and overlay the FilterBar
- [ ] Profile-details and tasks modals still open from the topbar ProfileMenu
- [ ] At 1280px viewport: full 240px sidebar with labels; at 1000px: 64px icon rail, labels hidden, links still navigate (title tooltips present)
- [ ] `document.body.scrollWidth <= window.innerWidth` at both viewports (no horizontal scroll)
- [ ] Switch locale to Japanese: all 7 translated nav labels render (Reports included)

## Key Reminders

1. Delegate ALL .vue edits to vue-expert when available
2. Inline SVG icons only — no emojis in the UI
3. Sidebar z-index stays at or below 100
4. FilterBar's `top: 70px` is the hidden coupling most likely to be missed — it must become `top: 0`
5. Preserve the global style block in App.vue (everything except the deleted nav rules) — all views depend on it
6. Slate palette only: #0f172a, #64748b, #e2e8f0, #f8fafc, accent #2563eb
7. Remove the old nav CSS rules; do not leave orphaned `.nav-container >` selectors
