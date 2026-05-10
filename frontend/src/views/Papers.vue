<template>
  <div>
    <a-card title="纸张耗材库存">
      <a-button type="primary" @click="showAddModal" style="margin-bottom: 16px;">新增纸张</a-button>
      <a-table :dataSource="papers" :columns="columns" rowKey="id" :pagination="{ pageSize: 20 }">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'stock'">
            <a-tag :color="record.stock <= record.threshold ? 'red' : 'green'">{{ record.stock }}</a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button size="small" @click="showEditModal(record)">编辑</a-button>
              <a-popconfirm title="确认删除？" @confirm="handleDelete(record.id)">
                <a-button size="small" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-modal v-model:open="modalVisible" :title="editingId ? '编辑纸张' : '新增纸张'" @ok="handleSave" width="600px">
      <a-form :model="form" layout="vertical">
        <a-form-item label="纸张名称" required>
          <a-input v-model:value="form.name" />
        </a-form-item>
        <a-form-item label="克重(g)" required>
          <a-input-number v-model:value="form.gram_weight" :min="1" style="width: 100%;" />
        </a-form-item>
        <a-form-item label="幅面" required>
          <a-input v-model:value="form.size" placeholder="如 全开/对开/4K" />
        </a-form-item>
        <a-form-item label="库存张数" required>
          <a-input-number v-model:value="form.stock" :min="0" style="width: 100%;" />
        </a-form-item>
        <a-form-item label="单张成本(元)" required>
          <a-input-number v-model:value="form.unit_cost" :min="0" :step="0.1" style="width: 100%;" />
        </a-form-item>
        <a-form-item label="库存告警阈值">
          <a-input-number v-model:value="form.threshold" :min="0" style="width: 100%;" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { message } from 'ant-design-vue'

const papers = ref([])
const modalVisible = ref(false)
const editingId = ref(null)
const form = ref({ name: '', gram_weight: 200, size: '', stock: 0, unit_cost: 0, threshold: 10 })

const columns = [
  { title: '纸张名称', dataIndex: 'name', key: 'name', width: 160 },
  { title: '克重(g)', dataIndex: 'gram_weight', key: 'gram_weight', width: 100 },
  { title: '幅面', dataIndex: 'size', key: 'size', width: 120 },
  { title: '库存张数', dataIndex: 'stock', key: 'stock', width: 100 },
  { title: '单张成本(元)', dataIndex: 'unit_cost', key: 'unit_cost', width: 120 },
  { title: '告警阈值', dataIndex: 'threshold', key: 'threshold', width: 100 },
  { title: '操作', key: 'action', width: 150 },
]

const fetchPapers = async () => {
  const { data } = await api.get('/papers/')
  papers.value = data
}

const showAddModal = () => {
  editingId.value = null
  form.value = { name: '', gram_weight: 200, size: '', stock: 0, unit_cost: 0, threshold: 10 }
  modalVisible.value = true
}

const showEditModal = (record) => {
  editingId.value = record.id
  form.value = { name: record.name, gram_weight: record.gram_weight, size: record.size, stock: record.stock, unit_cost: record.unit_cost, threshold: record.threshold }
  modalVisible.value = true
}

const handleSave = async () => {
  if (editingId.value) {
    await api.put(`/papers/${editingId.value}`, form.value)
    message.success('更新成功')
  } else {
    await api.post('/papers/', form.value)
    message.success('创建成功')
  }
  modalVisible.value = false
  fetchPapers()
}

const handleDelete = async (id) => {
  await api.delete(`/papers/${id}`)
  message.success('删除成功')
  fetchPapers()
}

onMounted(fetchPapers)
</script>
