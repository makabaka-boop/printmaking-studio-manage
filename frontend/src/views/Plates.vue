<template>
  <a-card title="版次信息管理">
    <template #extra>
      <a-button type="primary" @click="showModal = true">
        <PlusOutlined /> 新增版次
      </a-button>
    </template>

    <a-table :columns="columns" :data-source="plates" row-key="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'is_finalized'">
          <a-tag :color="record.is_finalized ? 'green' : 'orange'">
            {{ record.is_finalized ? '已定稿' : '草稿' }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-button type="link" @click="handleEdit(record)">编辑</a-button>
          <a-popconfirm title="确定删除?" @confirm="handleDelete(record.id)">
            <a-button type="link" danger>删除</a-button>
          </a-popconfirm>
        </template>
      </template>
    </a-table>

    <a-modal
      v-model:open="showModal"
      :title="editingId ? '编辑版次' : '新增版次'"
      @ok="handleSubmit"
      :confirm-loading="loading"
    >
      <a-form :model="form" layout="vertical">
        <a-form-item label="所属作品" required>
          <a-select v-model:value="form.artwork_id" placeholder="请选择作品" :disabled="!!editingId">
            <a-select-option v-for="a in artworks" :key="a.id" :value="a.id">
              {{ a.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="色版号" required>
          <a-input-number v-model:value="form.color_number" :min="1" style="width: 100%" />
        </a-form-item>
        <a-form-item label="油墨配比">
          <a-textarea v-model:value="form.ink_ratio" :rows="3" placeholder="油墨配比备注" />
        </a-form-item>
        <a-form-item label="是否定稿">
          <a-switch v-model:checked="form.is_finalized" />
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea v-model:value="form.notes" :rows="2" />
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

const plates = ref([])
const artworks = ref([])
const showModal = ref(false)
const loading = ref(false)
const editingId = ref(null)
const form = ref({
  artwork_id: null,
  color_number: 1,
  ink_ratio: '',
  is_finalized: false,
  notes: ''
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '作品ID', dataIndex: 'artwork_id', key: 'artwork_id', width: 80 },
  { title: '色版号', dataIndex: 'color_number', key: 'color_number', width: 80 },
  { title: '油墨配比', dataIndex: 'ink_ratio', key: 'ink_ratio', ellipsis: true },
  { title: '状态', key: 'is_finalized', width: 100 },
  { title: '备注', dataIndex: 'notes', key: 'notes', ellipsis: true },
  { title: '操作', key: 'action', width: 150 }
]

const loadData = async () => {
  const [platesRes, artworksRes] = await Promise.all([
    api.getPlates(),
    api.getArtworks()
  ])
  plates.value = platesRes.data
  artworks.value = artworksRes.data
}

const handleEdit = (record) => {
  editingId.value = record.id
  form.value = {
    artwork_id: record.artwork_id,
    color_number: record.color_number,
    ink_ratio: record.ink_ratio || '',
    is_finalized: record.is_finalized,
    notes: record.notes || ''
  }
  showModal.value = true
}

const handleSubmit = async () => {
  loading.value = true
  try {
    if (editingId.value) {
      await api.updatePlate(editingId.value, form.value)
      message.success('更新成功')
    } else {
      await api.createPlate(form.value)
      message.success('创建成功')
    }
    showModal.value = false
    editingId.value = null
    form.value = { artwork_id: null, color_number: 1, ink_ratio: '', is_finalized: false, notes: '' }
    loadData()
  } catch (error) {
    message.error('操作失败')
  } finally {
    loading.value = false
  }
}

const handleDelete = async (id) => {
  await api.deletePlate(id)
  message.success('删除成功')
  loadData()
}

onMounted(() => {
  loadData()
})
</script>
