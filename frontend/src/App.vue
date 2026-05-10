<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider v-model:collapsed="collapsed" collapsible theme="dark" width="220">
      <div class="logo">版画工作室</div>
      <a-menu v-model:selectedKeys="selectedKeys" theme="dark" mode="inline" @click="onMenuClick">
        <a-menu-item key="/">
          <template #icon><DashboardOutlined /></template>
          <span>仪表盘</span>
        </a-menu-item>
        <a-menu-item key="/artworks">
          <template #icon><PictureOutlined /></template>
          <span>作品档案</span>
        </a-menu-item>
        <a-menu-item key="/batches">
          <template #icon><PrinterOutlined /></template>
          <span>印制批次</span>
        </a-menu-item>
        <a-menu-item key="/papers">
          <template #icon><FileOutlined /></template>
          <span>纸张耗材</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header style="background: #fff; padding: 0 24px; font-size: 18px; font-weight: 600;">
        {{ currentTitle }}
      </a-layout-header>
      <a-layout-content style="margin: 16px;">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { DashboardOutlined, PictureOutlined, PrinterOutlined, FileOutlined } from '@ant-design/icons-vue'

const router = useRouter()
const route = useRoute()
const collapsed = ref(false)
const selectedKeys = ref([route.path])

const currentTitle = computed(() => route.meta.title || '版画工作室')

watch(() => route.path, (val) => {
  selectedKeys.value = [val]
})

const onMenuClick = ({ key }) => {
  router.push(key)
}
</script>

<style scoped>
.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 2px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
</style>
