import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/artworks',
    name: 'Artworks',
    component: () => import('../views/Artworks.vue')
  },
  {
    path: '/plates',
    name: 'Plates',
    component: () => import('../views/Plates.vue')
  },
  {
    path: '/papers',
    name: 'Papers',
    component: () => import('../views/Papers.vue')
  },
  {
    path: '/batches',
    name: 'Batches',
    component: () => import('../views/Batches.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
