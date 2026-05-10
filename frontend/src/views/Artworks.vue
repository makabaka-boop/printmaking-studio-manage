<template>
  <div>
    <a-card title="作品档案" style="margin-bottom: 16px;">
      <a-button type="primary" @click="showAddModal" style="margin-bottom: 16px;">新增作品</a-button>
      <a-table :dataSource="artworks" :columns="columns" rowKey="id" :pagination="{ pageSize: 20 }" :scroll="{ x: 1200 }">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button size="small" @click="showPlateModal(record)">版次管理</a-button>
              <a-button size="small" @click="showEditModal(record)">编辑</a-button>
              <a-popconfirm title="确认删除？" @confirm="handleDelete(record.id)">
                <a-button size="small" danger>删除</a-button>
              </a-popconfirm>
              <a-button size="small" type="link" @click="exportEdition(record.id)">导出台账</a-button>
            </a-space>
          </template>
          <template v-if="column.key === 'remaining_edition'">
            <a-tag :color="record.remaining_edition > 0 ? 'blue' : 'red'">{{ record.remaining_edition }}</a-tag>
          </template>
          <template v-if="column.key === 'print_type'">
            <a-tag>{{ record.print_type }}</a-tag>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-modal v-model:open="modalVisible" :title="editingId ? '编辑作品' : '新增作品'" @ok="handleSave" width="600px">
      <a-form :model="form" layout="vertical">
        <a-form-item label="作品名" required>
          <a-input v-model:value="form.name" />
        </a-form-item>
        <a-form-item label="版种" required>
          <a-select v-model:value="form.print_type" placeholder="选择版种">
            <a-select-option value="木刻">木刻</a-select-option>
            <a-select-option value="铜版">铜版</a-select-option>
            <a-select-option value="丝网">丝网</a-select-option>
            <a-select-option value="石版">石版</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="成品尺寸">
          <a-input v-model:value="form.size" placeholder="如 30×40cm" />
        </a-form-item>
        <a-form-item label="计划版数" required>
          <a-input-number v-model:value="form.planned_edition" :min="1" style="width: 100%;" />
        </a-form-item>
        <a-form-item label="签名规则">
          <a-input v-model:value="form.signature_rule" placeholder="如 ED 1/30" />
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal v-model:open="plateModalVisible" :title="'版次管理 - ' + plateArtworkName" width="800px" :footer="null">
      <a-button type="primary" size="small" @click="showAddPlate" style="margin-bottom: 12px;">新增版次</a-button>
      <a-table :dataSource="plates" :columns="plateColumns" rowKey="id" size="small" :pagination="false">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'is_finalized'">
            <a-tag :color="record.is_finalized ? 'green' : 'orange'">{{ record.is_finalized ? '已定稿' : '未定稿' }}</a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button size="small" @click="showEditPlate(record)">编辑</a-button>
              <a-popconfirm title="确认删除？" @confirm="handleDeletePlate(record.id)">
                <a-button size="small" danger>删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-modal>

    <a-modal v-model:open="plateFormVisible" :title="editingPlateId ? '编辑版次' : '新增版次'" @ok="handleSavePlate" width="500px">
      <a-form :model="plateForm" layout="vertical">
        <a-form-item label="第几色版" required>
          <a-input-number v-model:value="plateForm.color_order" :min="1" style="width: 100%;" />
        </a-form-item>
        <a-form-item label="油墨配比备注">
          <a-textarea v-model:value="plateForm.ink_ratio_note" :rows="3" />
        </a-form-item>
        <a-form-item label="是否已定稿">
          <a-switch v-model:checked="plateForm.is_finalized" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { message } from 'ant-design-vue'

const artworks = ref([])
const modalVisible = ref(false)
const editingId = ref(null)
const form = ref({ name: '', print_type: '', size: '', planned_edition: 30, signature_rule: '' })

const plateModalVisible = ref(false)
const plateFormVisible = ref(false)
const plates = ref([])
const plateArtworkId = ref(null)
const plateArtworkName = ref('')
const editingPlateId = ref(null)
const plateForm = ref({ color_order: 1, ink_ratio_note: '', is_finalized: false })

const columns = [
  { title: '作品名', dataIndex: 'name', key: 'name', width: 160 },
  { title: '版种', dataIndex: 'print_type', key: 'print_type', width: 100 },
  { title: '成品尺寸', dataIndex: 'size', key: 'size', width: 120 },
  { title: '计划版数', dataIndex: 'planned_edition', key: 'planned_edition', width: 100 },
  { title: '剩余可售版数', dataIndex: 'remaining_edition', key: 'remaining_edition', width: 130 },
  { title: '签名规则', dataIndex: 'signature_rule', key: 'signature_rule', width: 140 },
  { title: '操作', key: 'action', width: 260, fixed: 'right' },
]

const plateColumns = [
  { title: '色版序号', dataIndex: 'color_order', key: 'color_order', width: 100 },
  { title: '油墨配比备注', dataIndex: 'ink_ratio_note', key: 'ink_ratio_note' },
  { title: '定稿状态', dataIndex: 'is_finalized', key: 'is_finalized', width: 120 },
  { title: '操作', key: 'action', width: 150 },
]

const fetchArtworks = async () => {
  const { data } = await api.get('/artworks/')
  artworks.value = data
}

const showAddModal = () => {
  editingId.value = null
  form.value = { name: '', print_type: '', size: '', planned_edition: 30, signature_rule: '' }
  modalVisible.value = true
}

const showEditModal = (record) => {
  editingId.value = record.id
  form.value = { name: record.name, print_type: record.print_type, size: record.size, planned_edition: record.planned_edition, signature_rule: record.signature_rule }
  modalVisible.value = true
}

const handleSave = async () => {
  if (editingId.value) {
    await api.put(`/artworks/${editingId.value}`, form.value)
    message.success('更新成功')
  } else {
    await api.post('/artworks/', form.value)
    message.success('创建成功')
  }
  modalVisible.value = false
  fetchArtworks()
}

const handleDelete = async (id) => {
  await api.delete(`/artworks/${id}`)
  message.success('删除成功')
  fetchArtworks()
}

const exportEdition = (id) => {
  window.open(`/api/export/edition/${id}`, '_blank')
}

const showPlateModal = async (record) => {
  plateArtworkId.value = record.id
  plateArtworkName.value = record.name
  const { data } = await api.get(`/artworks/${record.id}/plates`)
  plates.value = data
  plateModalVisible.value = true
}

const showAddPlate = () => {
  editingPlateId.value = null
  plateForm.value = { color_order: plates.value.length + 1, ink_ratio_note: '', is_finalized: false }
  plateFormVisible.value = true
}

const showEditPlate = (record) => {
  editingPlateId.value = record.id
  plateForm.value = { color_order: record.color_order, ink_ratio_note: record.ink_ratio_note, is_finalized: record.is_finalized }
  plateFormVisible.value = true
}

const handleSavePlate = async () => {
  if (editingPlateId.value) {
    await api.put(`/artworks/plates/${editingPlateId.value}`, { ...plateForm.value, artwork_id: plateArtworkId.value })
    message.success('版次更新成功')
  } else {
    await api.post(`/artworks/${plateArtworkId.value}/plates`, { ...plateForm.value, artwork_id: plateArtworkId.value })
    message.success('版次创建成功')
  }
  plateFormVisible.value = false
  const { data } = await api.get(`/artworks/${plateArtworkId.value}/plates`)
  plates.value = data
}

const handleDeletePlate = async (id) => {
  await api.delete(`/artworks/plates/${id}`)
  message.success('版次删除成功')
  const { data } = await api.get(`/artworks/${plateArtworkId.value}/plates`)
  plates.value = data
}

onMounted(fetchArtworks)
</script>
