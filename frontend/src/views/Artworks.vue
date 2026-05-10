<template>
  <div>
    <a-page-header title="作品管理" style="margin-bottom: 24px">
      <template #extra>
        <a-button type="primary" @click="handleAdd">
          <plus-outlined />
          新建作品
        </a-button>
      </template>
    </a-page-header>

    <a-table :columns="columns" :data-source="artworks" :loading="loading" row-key="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'print_type'">
          <a-tag>{{ record.print_type }}</a-tag>
        </template>
        <template v-else-if="column.key === 'progress'">
          <a-progress :percent="record.planned_edition > 0 ? Math.min(100, Math.round(record.sold_edition / record.planned_edition * 100)) : 0" size="small" />
        </template>
        <template v-else-if="column.key === 'remaining'">
          <span :style="{ color: record.remaining_edition <= 0 ? '#ff4d4f' : '#52c41a', fontWeight: 'bold' }">
            {{ record.remaining_edition }}
          </span>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-button-group>
            <a-button size="small" @click="handleEdit(record)">编辑</a-button>
            <a-button size="small" @click="handleViewPlates(record)">版次</a-button>
            <a-button size="small" @click="handleExport(record)">导出台账</a-button>
            <a-popconfirm title="确定删除？" @confirm="handleDelete(record.id)">
              <a-button size="small" danger>删除</a-button>
            </a-popconfirm>
          </a-button-group>
        </template>
      </template>
    </a-table>

    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑作品' : '新建作品'"
      @ok="handleSubmit"
      @cancel="modalVisible = false"
      :confirm-loading="submitting"
    >
      <a-form :model="formData" :label-col="{ span: 4 }" :wrapper-col="{ span: 18 }">
        <a-form-item label="作品名称" required>
          <a-input v-model:value="formData.name" placeholder="请输入作品名称" />
        </a-form-item>
        <a-form-item label="版种" required>
          <a-select v-model:value="formData.print_type" placeholder="请选择版种">
            <a-select-option value="木刻">木刻</a-select-option>
            <a-select-option value="铜版">铜版</a-select-option>
            <a-select-option value="丝网">丝网</a-select-option>
            <a-select-option value="石版">石版</a-select-option>
            <a-select-option value="其他">其他</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="成品尺寸">
          <a-input v-model:value="formData.finished_size" placeholder="如：30cm x 40cm" />
        </a-form-item>
        <a-form-item label="计划版数" required>
          <a-input-number v-model:value="formData.planned_edition" :min="1" style="width: 100%" />
        </a-form-item>
        <a-form-item label="签名规则">
          <a-textarea v-model:value="formData.signature_rule" :rows="3" placeholder="描述签名规则" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { PlusOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { artworksApi } from '@/api'

const router = useRouter()

const artworks = ref([])
const loading = ref(false)
const modalVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formData = ref({
  id: null,
  name: '',
  print_type: '',
  finished_size: '',
  planned_edition: 50,
  signature_rule: ''
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '作品名称', dataIndex: 'name', key: 'name' },
  { title: '版种', dataIndex: 'print_type', key: 'print_type' },
  { title: '成品尺寸', dataIndex: 'finished_size', key: 'finished_size' },
  { title: '计划版数', dataIndex: 'planned_edition', key: 'planned_edition' },
  { title: '已印制', dataIndex: 'sold_edition', key: 'sold_edition' },
  { title: '完成度', dataIndex: 'progress', key: 'progress' },
  { title: '剩余可售', dataIndex: 'remaining', key: 'remaining' },
  { title: '操作', key: 'action', width: 260, fixed: 'right' }
]

const loadData = async () => {
  loading.value = true
  try {
    artworks.value = await artworksApi.list()
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  formData.value = {
    id: null,
    name: '',
    print_type: '',
    finished_size: '',
    planned_edition: 50,
    signature_rule: ''
  }
  modalVisible.value = true
}

const handleEdit = (record) => {
  isEdit.value = true
  formData.value = { ...record }
  modalVisible.value = true
}

const handleSubmit = async () => {
  if (!formData.value.name || !formData.value.print_type) {
    message.warning('请填写必填项')
    return
  }
  submitting.value = true
  try {
    if (isEdit.value) {
      await artworksApi.update(formData.value.id, formData.value)
      message.success('更新成功')
    } else {
      await artworksApi.create(formData.value)
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
    await artworksApi.delete(id)
    message.success('删除成功')
    loadData()
  } catch (error) {
    console.error(error)
  }
}

const handleViewPlates = (record) => {
  router.push({ path: '/plates', query: { artwork_id: record.id } })
}

const handleExport = (record) => {
  artworksApi.export(record.id)
}

onMounted(() => {
  loadData()
})
</script>
