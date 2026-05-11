<template>
  <a-card title="作品档案管理">
    <template #extra>
      <a-button type="primary" @click="showModal = true">
        <PlusOutlined /> 新增作品
      </a-button>
    </template>

    <a-table :columns="columns" :data-source="artworks" row-key="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'print_type'">
          <a-tag color="blue">{{ record.print_type }}</a-tag>
        </template>
        <template v-else-if="column.key === 'progress'">
          <a-progress
            :percent="Math.round((record.sold_count / record.planned_edition) * 100)"
            size="small"
          />
        </template>
        <template v-else-if="column.key === 'action'">
          <a-button type="link" @click="exportEdition(record.id)">导出台账</a-button>
          <a-popconfirm title="确定删除?" @confirm="handleDelete(record.id)">
            <a-button type="link" danger>删除</a-button>
          </a-popconfirm>
        </template>
      </template>
    </a-table>

    <a-modal
      v-model:open="showModal"
      title="新增作品"
      @ok="handleSubmit"
      :confirm-loading="loading"
    >
      <a-form :model="form" layout="vertical">
        <a-form-item label="作品名称" required>
          <a-input v-model:value="form.name" placeholder="请输入作品名称" />
        </a-form-item>
        <a-form-item label="版种" required>
          <a-select v-model:value="form.print_type" placeholder="请选择版种">
            <a-select-option value="木刻">木刻</a-select-option>
            <a-select-option value="铜版">铜版</a-select-option>
            <a-select-option value="丝网">丝网</a-select-option>
            <a-select-option value="石版">石版</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="成品尺寸">
          <a-input v-model:value="form.finished_size" placeholder="如：30x40cm" />
        </a-form-item>
        <a-form-item label="计划版数" required>
          <a-input-number v-model:value="form.planned_edition" :min="1" style="width: 100%" />
        </a-form-item>
        <a-form-item label="签名规则">
          <a-textarea v-model:value="form.signature_rule" :rows="3" placeholder="签名规则占位" />
        </a-form-item>
      </a-form>
    </a-modal>
  </a-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import api from '../api'

const artworks = ref([])
const showModal = ref(false)
const loading = ref(false)
const form = ref({
  name: '',
  print_type: '',
  finished_size: '',
  planned_edition: 10,
  signature_rule: ''
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '作品名称', dataIndex: 'name', key: 'name' },
  { title: '版种', key: 'print_type' },
  { title: '成品尺寸', dataIndex: 'finished_size', key: 'finished_size' },
  { title: '计划版数', dataIndex: 'planned_edition', key: 'planned_edition' },
  { title: '已印制', dataIndex: 'sold_count', key: 'sold_count' },
  { title: '剩余可售', dataIndex: 'remaining_edition', key: 'remaining_edition' },
  { title: '进度', key: 'progress' },
  { title: '操作', key: 'action', width: 150 }
]

const loadData = async () => {
  const res = await api.getArtworks()
  artworks.value = res.data
}

const handleSubmit = async () => {
  if (!form.value.name || !form.value.print_type) {
    message.warning('请填写必填项')
    return
  }
  loading.value = true
  try {
    await api.createArtwork(form.value)
    message.success('创建成功')
    showModal.value = false
    form.value = { name: '', print_type: '', finished_size: '', planned_edition: 10, signature_rule: '' }
    loadData()
  } catch (error) {
    message.error('创建失败')
  } finally {
    loading.value = false
  }
}

const handleDelete = async (id) => {
  await api.deleteArtwork(id)
  message.success('删除成功')
  loadData()
}

const exportEdition = (id) => {
  api.exportEdition(id)
}

onMounted(() => {
  loadData()
})
</script>
