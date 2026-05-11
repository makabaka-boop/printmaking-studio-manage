<template>
  <a-card title="纸张与耗材库存">
    <template #extra>
      <a-button type="primary" @click="showModal = true">
        <PlusOutlined /> 新增纸张
      </a-button>
    </template>

    <a-table :columns="columns" :data-source="papers" row-key="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'stock_status'">
          <a-tag :color="record.is_low_stock ? 'red' : 'green'">
            {{ record.is_low_stock ? '库存不足' : '充足' }}
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
      :title="editingId ? '编辑纸张' : '新增纸张'"
      @ok="handleSubmit"
      :confirm-loading="loading"
    >
      <a-form :model="form" layout="vertical">
        <a-form-item label="纸张名称" required>
          <a-input v-model:value="form.name" placeholder="请输入纸张名称" />
        </a-form-item>
        <a-form-item label="克重(g)">
          <a-input-number v-model:value="form.weight" :min="0" style="width: 100%" />
        </a-form-item>
        <a-form-item label="幅面">
          <a-input v-model:value="form.size" placeholder="如：A4、全开" />
        </a-form-item>
        <a-form-item label="库存张数" required>
          <a-input-number v-model:value="form.stock_count" :min="0" style="width: 100%" />
        </a-form-item>
        <a-form-item label="单张成本(元)">
          <a-input-number v-model:value="form.cost_per_sheet" :min="0" :step="0.01" style="width: 100%" />
        </a-form-item>
        <a-form-item label="预警阈值">
          <a-input-number v-model:value="form.threshold" :min="0" style="width: 100%" />
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

const papers = ref([])
const showModal = ref(false)
const loading = ref(false)
const editingId = ref(null)
const form = ref({
  name: '',
  weight: null,
  size: '',
  stock_count: 0,
  cost_per_sheet: null,
  threshold: 50
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '纸张名称', dataIndex: 'name', key: 'name' },
  { title: '克重', dataIndex: 'weight', key: 'weight' },
  { title: '幅面', dataIndex: 'size', key: 'size' },
  { title: '库存张数', dataIndex: 'stock_count', key: 'stock_count' },
  { title: '单张成本', dataIndex: 'cost_per_sheet', key: 'cost_per_sheet' },
  { title: '阈值', dataIndex: 'threshold', key: 'threshold' },
  { title: '状态', key: 'stock_status', width: 100 },
  { title: '操作', key: 'action', width: 150 }
]

const loadData = async () => {
  const res = await api.getPapers()
  papers.value = res.data
}

const handleEdit = (record) => {
  editingId.value = record.id
  form.value = {
    name: record.name,
    weight: record.weight,
    size: record.size || '',
    stock_count: record.stock_count,
    cost_per_sheet: record.cost_per_sheet,
    threshold: record.threshold
  }
  showModal.value = true
}

const handleSubmit = async () => {
  if (!form.value.name) {
    message.warning('请填写必填项')
    return
  }
  loading.value = true
  try {
    if (editingId.value) {
      await api.updatePaper(editingId.value, form.value)
      message.success('更新成功')
    } else {
      await api.createPaper(form.value)
      message.success('创建成功')
    }
    showModal.value = false
    editingId.value = null
    form.value = { name: '', weight: null, size: '', stock_count: 0, cost_per_sheet: null, threshold: 50 }
    loadData()
  } catch (error) {
    message.error('操作失败')
  } finally {
    loading.value = false
  }
}

const handleDelete = async (id) => {
  await api.deletePaper(id)
  message.success('删除成功')
  loadData()
}

onMounted(() => {
  loadData()
})
</script>
