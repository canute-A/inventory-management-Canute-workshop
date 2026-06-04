import { ref } from 'vue'

const stored = localStorage.getItem('sidebar-collapsed')
const isCollapsed = ref(stored === 'true')

export function useSidebar() {
  const toggleSidebar = () => {
    isCollapsed.value = !isCollapsed.value
    localStorage.setItem('sidebar-collapsed', String(isCollapsed.value))
  }

  return {
    isCollapsed,
    toggleSidebar
  }
}
