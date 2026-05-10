<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider v-model:collapsed="collapsed" collapsible>
      <div class="logo">
        <h2 style="color: white; text-align: center; padding: 20px 0">{{ collapsed ? '版画' : '版画工作室' }}</h2>
      </div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="inline"
        @click="handleMenuClick"
      >
        <a-menu-item key="/dashboard">
          <dashboard-outlined />
          <span>仪表盘</span>
        </a-menu-item>
        <a-menu-item key="/artworks">
          <picture-outlined />
          <span>作品管理</span>
        </a-menu-item>
        <a-menu-item key="/plates">
          <layout-outlined />
          <span>版次管理</span>
        </a-menu-item>
        <a-menu-item key="/papers">
          <file-text-outlined />
          <span>纸张库存</span>
        </a-menu-item>
        <a-menu-item key="/batches">
          <printer-outlined />
          <span>印制批次</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header style="background: #fff; padding: 0 24px">
        <span style="font-size: 18px; font-weight: bold">手工版画工作室管理平台</span>
      </a-layout-header>
      <a-layout-content style="margin: 24px 16px; padding: 24px; background: #fff">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  DashboardOutlined,
  PictureOutlined,
  LayoutOutlined,
  FileTextOutlined,
  PrinterOutlined
} from '@ant-design/icons-vue'

const collapsed = ref(false)
const selectedKeys = ref(['/dashboard'])
const route = useRoute()
const router = useRouter()

onMounted(() => {
  selectedKeys.value = [route.path]
})

const handleMenuClick = ({ key }) => {
  router.push(key)
}
</script>

<style scoped>
.logo {
  height: 64px;
  margin: 0;
  background: #001529;
}
</style>
