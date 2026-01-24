import { createRouter, createWebHistory } from 'vue-router'
import DashboardPage from '../pages/DashboardPage.vue'
import DevicesPage from '../pages/DevicesPage.vue'
import NetworkScanPage from '../pages/NetworkScanPage.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../pages/AboutPage.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardPage
  },
  {
    path: '/devices',
    name: 'Devices',
    component: DevicesPage
  },
  {
    path: '/devices/:deviceId',
    name: 'Device Details',
    component: () => import('../pages/DeviceDetailsPage.vue')
  },
  {
    path: '/network-scan',
    name: 'Network Scan',
    component: NetworkScanPage
  },
  {
    path: '/backups',
    name: 'Backups',
    component: () => import('../pages/BackupsPage.vue')
  },
  {
    path: '/secrets',
    name: 'Secrets',
    component: () => import('../pages/SecretsPage.vue')
  },
  {
    path: '/app-config',
    name: 'App Config',
    component: () => import('../pages/AppConfigPage.vue')
  },
  {
    path: '/backups/compare-backups',
    name: 'Backup Compare',
    component: () => import('../pages/BackupComparePage.vue')
  },
  {
    path: '/backups/compare-configs',
    name: 'Config Compare',
    component: () => import('../pages/ConfigComparePage.vue')
  },
  {
    path: '/schedulers',
    name: 'Schedulers',
    component: () => import('../pages/SchedulerPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
