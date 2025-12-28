import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import ContactsView from '../views/ContactsView.vue'
import CompaniesView from '../views/CompaniesView.vue'
import DealsView from '../views/DealsView.vue'
import TasksView from '../views/TasksView.vue'
import AuditLogsView from '../views/AuditLogsView.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresGuest: true }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/contacts',
    name: 'Contacts',
    component: ContactsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/companies',
    name: 'Companies',
    component: CompaniesView,
    meta: { requiresAuth: true }
  },
  {
    path: '/deals',
    name: 'Deals',
    component: DealsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: TasksView,
    meta: { requiresAuth: true }
  },
  {
    path: '/audit-logs',
    name: 'AuditLogs',
    component: AuditLogsView,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const isAuthenticated = !!token

  console.log('Router navigation:', from.path, '->', to.path, 'Authenticated:', isAuthenticated)

  if (to.meta.requiresAuth && !isAuthenticated) {
    console.log('Redirecting to login - not authenticated')
    next('/login')
  } else if (to.meta.requiresGuest && isAuthenticated) {
    console.log('Redirecting to dashboard - already authenticated')
    next('/')
  } else {
    console.log('Allowing navigation')
    next()
  }
})

router.afterEach((to, from) => {
  console.log('Navigation completed:', to.path)
  document.title = `${to.name || 'Page'} - Mini CRM`
})

export default router
