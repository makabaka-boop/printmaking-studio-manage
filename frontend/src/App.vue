<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider v-model:collapsed="collapsed" collapsible theme="dark">
      <div class="logo">
        <h2 style="color: white; text-align: center; padding: 16px 0">
          {{ collapsed ? '版画' : '版画工作室' }}
        </h2>
      </div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="inline"
        @click="handleMenuClick"
      >
        <a-menu-item key="/">
          <template #icon><DashboardOutlined /></template>
          <span>仪表盘</span>
        </a-menu-item>
        <a-menu-item key="/artworks">
          <template #icon><PictureOutlined /></template>
          <span>作品档案</span>
        </a-menu-item>
        <a-menu-item key="/plates">
          <template #icon><AppstoreOutlined /></template>
          <span>版次管理</span>
        </a-menu-item>
        <a-menu-item key="/papers">
          <template #icon><FileTextOutlined /></template>
          <span>纸张库存</span>
        </a-menu-item>
        <a-menu-item key="/batches">
          <template #icon><OrderedListOutlined /></template>
          <span>印制批次</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header style="background: #fff; padding: 0 24px">
        <h1 style="margin: 0">手工版画工作室管理系统</h1>
      </a-layout-header>
      <a-layout-content style="margin: 24px">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  DashboardOutlined,
  PictureOutlined,
  AppstoreOutlined,
  FileTextOutlined,
  OrderedListOutlined
} from '@ant-design/icons-vue'

const collapsed = ref(false)
const selectedKeys = ref(['/'])
const router = useRouter()
const route = useRoute()

onMounted(() => {
  selectedKeys.value = [route.path]
})

const handleMenuClick = ({ key }) => {
  router.push(key)
  selectedKeys.value = [key]
}
</script>

<style>
.logo {
  height: 64px;
  margin: 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
}
</style>
