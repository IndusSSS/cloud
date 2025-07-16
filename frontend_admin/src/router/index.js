import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// Views
import LoginView from '../views/LoginView.vue'
import Dashboard from '../views/Dashboard.vue'

// Lazy-loaded views
const UsersView = () => import('../views/UsersView.vue')
const DevicesView = () => import('../views/DevicesView.vue')
const TenantsView = () => import('../views/TenantsView.vue')
const HealthView = () => import('../views/HealthView.vue')
const SettingsView = () => import('../views/SettingsView.vue')
const AuditView = () => import('../views/AuditView.vue')

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
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'Users',
    component: UsersView,
    meta: { requiresAuth: true }
  },
  {
    path: '/devices',
    name: 'Devices',
    component: DevicesView,
    meta: { requiresAuth: true }
  },
  {
    path: '/tenants',
    name: 'Tenants',
    component: TenantsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/health',
    name: 'Health',
    component: HealthView,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/audit',
    name: 'Audit',
    component: AuditView,
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }
  
  // Check if route requires guest (not authenticated)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/')
    return
  }
  
  next()
})

export default router 