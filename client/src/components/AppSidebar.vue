<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-logo">
      <span class="logo-monogram">CC</span>
      <div class="logo-text">
        <h1>{{ t('nav.companyName') }}</h1>
        <span class="subtitle">{{ t('nav.subtitle') }}</span>
      </div>
    </div>
    <nav class="sidebar-nav">
      <router-link to="/" :class="{ active: $route.path === '/' }" :title="t('nav.overview')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
          <rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>
        </svg>
        <span class="nav-label">{{ t('nav.overview') }}</span>
      </router-link>
      <router-link to="/inventory" :class="{ active: $route.path === '/inventory' }" :title="t('nav.inventory')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 8l-9-5-9 5v8l9 5 9-5V8z"/><path d="M3 8l9 5 9-5"/><path d="M12 13v8"/>
        </svg>
        <span class="nav-label">{{ t('nav.inventory') }}</span>
      </router-link>
      <router-link to="/orders" :class="{ active: $route.path === '/orders' }" :title="t('nav.orders')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 3h6a1 1 0 011 1v1h3a1 1 0 011 1v14a1 1 0 01-1 1H5a1 1 0 01-1-1V6a1 1 0 011-1h3V4a1 1 0 011-1z"/>
          <path d="M9 12h6M9 16h4"/>
        </svg>
        <span class="nav-label">{{ t('nav.orders') }}</span>
      </router-link>
      <router-link to="/spending" :class="{ active: $route.path === '/spending' }" :title="t('nav.finance')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="9"/><path d="M14.5 9.5c-.5-1-1.5-1.5-2.5-1.5-1.5 0-2.5 1-2.5 2 0 2.5 5 1.5 5 4 0 1-1 2-2.5 2-1 0-2-.5-2.5-1.5M12 6.5v11"/>
        </svg>
        <span class="nav-label">{{ t('nav.finance') }}</span>
      </router-link>
      <router-link to="/demand" :class="{ active: $route.path === '/demand' }" :title="t('nav.demandForecast')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>
        </svg>
        <span class="nav-label">{{ t('nav.demandForecast') }}</span>
      </router-link>
      <router-link to="/restocking" :class="{ active: $route.path === '/restocking' }" :title="t('nav.restocking')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12a9 9 0 11-2.64-6.36"/><path d="M21 3v6h-6"/>
        </svg>
        <span class="nav-label">{{ t('nav.restocking') }}</span>
      </router-link>
      <router-link to="/reports" :class="{ active: $route.path === '/reports' }" :title="t('nav.reports')">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/><path d="M14 2v6h6"/><path d="M9 13h6M9 17h6"/>
        </svg>
        <span class="nav-label">{{ t('nav.reports') }}</span>
      </router-link>
    </nav>
    <button
      class="collapse-toggle"
      :title="isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      :aria-label="isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      :aria-expanded="String(!isCollapsed)"
      @click="toggleSidebar"
    >
      <svg class="nav-icon toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M15 6l-6 6 6 6"/>
      </svg>
    </button>
  </aside>
</template>

<script>
import { useI18n } from '../composables/useI18n'
import { useSidebar } from '../composables/useSidebar'

export default {
  name: 'AppSidebar',
  setup() {
    const { t } = useI18n()
    const { isCollapsed, toggleSidebar } = useSidebar()
    return { t, isCollapsed, toggleSidebar }
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
  min-height: 70px;
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
  flex-shrink: 0;
}

.logo-text h1 {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.025em;
}

.logo-text .subtitle {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0.75rem 0.5rem;
}

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
  transition: all 0.15s ease;
}

.sidebar-nav a:hover {
  background: var(--color-bg);
  color: var(--color-text);
}

.sidebar-nav a.active {
  background: var(--color-accent-bg);
  color: var(--color-accent);
  border-left-color: var(--color-accent);
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.collapse-toggle {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem;
  margin: auto 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: white;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.collapse-toggle:hover {
  background: var(--color-bg);
  color: var(--color-text);
}

.toggle-icon {
  transition: transform 0.2s ease;
}

.sidebar.collapsed .toggle-icon {
  transform: rotate(180deg);
}

/* Manual collapse (toggle button) */
.sidebar.collapsed .nav-label,
.sidebar.collapsed .logo-text {
  display: none;
}

.sidebar.collapsed .logo-monogram {
  display: flex;
}

.sidebar.collapsed .sidebar-logo {
  justify-content: center;
  padding: 1rem 0.5rem;
}

.sidebar.collapsed .sidebar-nav a {
  justify-content: center;
  padding: 0.6rem;
}

/* Auto collapse at the tablet breakpoint (same rail look, forced by viewport) */
@media (max-width: 1024px) {
  .nav-label,
  .logo-text {
    display: none;
  }

  .logo-monogram {
    display: flex;
  }

  .sidebar-logo {
    justify-content: center;
    padding: 1rem 0.5rem;
  }

  .sidebar-nav a {
    justify-content: center;
    padding: 0.6rem;
  }

  .collapse-toggle {
    display: none; /* viewport forces the rail; manual toggle only applies on desktop */
  }
}
</style>
