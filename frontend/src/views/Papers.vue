<template>
  <div>
    <a-page-header title="纸张库存" style="margin-bottom: 24px">
      <template #extra>
        <a-button style="margin-right: 12px" @click="showOnlyLowStock = !showOnlyLowStock">
          <warning-outlined />
          {{ showOnlyLowStock ? '显示全部' : '仅显示预警' }}
        </a-button>
        <a-button type="primary" @click="handleAdd">
          <plus-outlined />
          新增纸张
        </a-button>
      </template>
    </a-page-header>

    <a-table :columns="columns" :data-source="papers" :loading="loading" row-key="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'stock'">
          <a-tag :color="record.is_low_stock ? 'red' : 'green'">
            {{ record.stock }} 张
          </a-tag>
        </template>
        <template v-else-if="column.key === 'cost'">
          ¥{{ record.cost_per_sheet.toFixed(2) }}
        </template>
        <template v-else-if="column.key === 'is_low'">
          <a-badge :status="record.is_low_stock ? 'error' : 'success'" :text="record.is_low_stock ? '库存不足' : '充足'" />
        </template>
        <template v-else-if="column.key === 'action'">
          <a-button-group>
            <a-button size="small" @click="handleEdit(record)">编辑</a-button>
            <a-popconfirm title="确定删除？" @confirm="handleDelete(record.id)">
              <a-button size="small" danger>删除</a-button>
            </a-popconfirm>
          </a-button-group>
        </template>
      </template>
    </a-table>

    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑纸张' : '新增纸张'"
      @ok="handleSubmit"
      @cancel="modalVisible = false"
      :confirm-loading="submitting"
    >
      <a-form :model="formData" :label-col="{ span: 4 }" :wrapper-col="{ span: 18 }">
        <a-form-item label="纸张名称" required>
          <a-input v-model:value="formData.name" placeholder="如：日本版画纸" />
        </a-form-item>
        <a-form-item label="克重">
          <a-input-number v-model:value="formData.weight" :min="0" style="width: 100%" addon-after="g" />
        </a-form-item>
        <a-form-item label="幅面">
          <a-input v-model:value="formData.size" placeholder="如：A3 / 70x100cm" />
        </a-form-item>
        <a-form-item label="库存张数">
          <a-input-number v-model:value="formData.stock" :min="0" style="width: 100%" />
        </a-form-item>
        <a-form-item label="单张成本">
          <a-input-number v-model:value="formData.cost_per_sheet" :min="0" :step="0.01" style="width: 100%" addon-before="¥" />
        </a-form-item>
        <a-form-item label="预警阈值">
          <a-input-number v-model:value="formData.threshold" :min="1" style="width: 100%" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { PlusOutlined, WarningOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { papersApi } from '@/api'

const papers = ref([])
const allPapers = ref([])
const loading = ref(false)
const modalVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const showOnlyLowStock = ref(false)
const formData = ref({
  id: null,
  name: '',
  weight: null,
  size: '',
  stock: 0,
  cost_per_sheet: 0,
  threshold: 50
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '纸张名称', dataIndex: 'name', key: 'name' },
  { title: '克重', dataIndex: 'weight', key: 'weight', customRender: ({ record }) => record.weight ? `${record.weight}g` : '-' },
  { title: '幅面', dataIndex: 'size', key: 'size' },
  { title: '库存', dataIndex: 'stock', key: 'stock' },
  { title: '单张成本', dataIndex: 'cost', key: 'cost' },
  { title: '阈值', dataIndex: 'threshold', key: 'threshold' },
  { title: '状态', dataIndex: 'is_low', key: 'is_low' },
  { title: '操作', key: 'action', width: 150, fixed: 'right' }
]

const loadData = async () => {
  loading.value = true
  try {
    allPapers.value = await papersApi.list()
    filterPapers()
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const filterPapers = () => {
  if (showOnlyLowStock.value) {
    papers.value = allPapers.value.filter(p => p.is_low_stock)
  } else {
    papers.value = [...allPapers.value]
  }
}

watch(showOnlyLowStock, () => {
  filterPapers()
})

const handleAdd = () => {
  isEdit.value = false
  formData.value = {
    id: null,
    name: '',
    weight: null,
    size: '',
    stock: 0,
    cost_per_sheet: 0,
    threshold: 50
  }
  modalVisible.value = true
}

const handleEdit = (record) => {
  isEdit.value = true
  formData.value = { ...record }
  modalVisible.value = true
}

const handleSubmit = async () => {
  if (!formData.value.name) {
    message.warning('请填写纸张名称')
    return
  }
  submitting.value = true
  try {
    if (isEdit.value) {
      await papersApi.update(formData.value.id, formData.value)
      message.success('更新成功')
    } else {
      await papersApi.create(formData.value)
      message.success('创建成功')
    }
    modalVisible.value = false
    loadData()
  } catch (error) {
    console.error(error)
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await papersApi.delete(id)
    message.success('删除成功')
    loadData()
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  loadData()
})
</script>
