import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/components/Layout.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'artworks',
        name: 'Artworks',
        component: () => import('@/views/Artworks.vue'),
        meta: { title: '作品管理' }
      },
      {
        path: 'plates',
        name: 'Plates',
        component: () => import('@/views/Plates.vue'),
        meta: { title: '版次管理' }
      },
      {
        path: 'papers',
        name: 'Papers',
        component: () => import('@/views/Papers.vue'),
        meta: { title: '纸张库存' }
      },
      {
        path: 'batches',
        name: 'Batches',
        component: () => import('@/views/Batches.vue'),
        meta: { title: '印制批次' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '手工版画工作室管理平台'
  next()
})

export default router
