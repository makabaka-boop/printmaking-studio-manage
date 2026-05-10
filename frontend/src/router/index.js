import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '仪表盘' } },
  { path: '/artworks', name: 'Artworks', component: () => import('../views/Artworks.vue'), meta: { title: '作品档案' } },
  { path: '/batches', name: 'Batches', component: () => import('../views/Batches.vue'), meta: { title: '印制批次' } },
  { path: '/papers', name: 'Papers', component: () => import('../views/Papers.vue'), meta: { title: '纸张耗材' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  document.title = to.meta.title + ' - 版画工作室管理平台'
})

export default router
