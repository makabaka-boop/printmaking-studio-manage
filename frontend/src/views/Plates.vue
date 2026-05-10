<template>
  <div>
    <a-page-header title="版次管理" style="margin-bottom: 24px">
      <template #extra>
        <a-select
          v-model:value="selectedArtworkId"
          placeholder="选择作品筛选"
          style="width: 200px; margin-right: 12px"
          allow-clear
          @change="loadData"
        >
          <a-select-option v-for="artwork in artworks" :key="artwork.id" :value="artwork.id">
            {{ artwork.name }}
          </a-select-option>
        </a-select>
        <a-button type="primary" @click="handleAdd">
          <plus-outlined />
          新版次
        </a-button>
      </template>
    </a-page-header>

    <a-table :columns="columns" :data-source="plates" :loading="loading" row-key="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'artwork_name'">
          {{ getArtworkName(record.artwork_id) }}
        </template>
        <template v-else-if="column.key === 'color_number'">
          <a-badge :count="record.color_number" :number-style="{ backgroundColor: '#1890ff' }" />
        </template>
        <template v-else-if="column.key === 'is_finalized'">
          <a-tag :color="record.is_finalized ? 'green' : 'default'">
            {{ record.is_finalized ? '已定稿' : '草稿' }}
          </a-tag>
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
      :title="isEdit ? '编辑版次' : '新版次'"
      @ok="handleSubmit"
      @cancel="modalVisible = false"
      :confirm-loading="submitting"
    >
      <a-form :model="formData" :label-col="{ span: 4 }" :wrapper-col="{ span: 18 }">
        <a-form-item label="所属作品" required>
          <a-select v-model:value="formData.artwork_id" placeholder="请选择作品">
            <a-select-option v-for="artwork in artworks" :key="artwork.id" :value="artwork.id">
              {{ artwork.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="色版序号" required>
          <a-input-number v-model:value="formData.color_number" :min="1" style="width: 100%" />
        </a-form-item>
        <a-form-item label="油墨配比">
          <a-textarea v-model:value="formData.ink_ratio" :rows="3" placeholder="如：品红70% + 黄30%" />
        </a-form-item>
        <a-form-item label="是否定稿">
          <a-switch v-model:checked="formData.is_finalized" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { PlusOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { platesApi, artworksApi } from '@/api'

const route = useRoute()

const plates = ref([])
const artworks = ref([])
const loading = ref(false)
const modalVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const selectedArtworkId = ref(null)
const formData = ref({
  id: null,
  artwork_id: null,
  color_number: 1,
  ink_ratio: '',
  is_finalized: false
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '作品', dataIndex: 'artwork_name', key: 'artwork_name' },
  { title: '色版序号', dataIndex: 'color_number', key: 'color_number' },
  { title: '油墨配比', dataIndex: 'ink_ratio', key: 'ink_ratio' },
  { title: '状态', dataIndex: 'is_finalized', key: 'is_finalized' },
  { title: '操作', key: 'action', width: 150, fixed: 'right' }
]

const getArtworkName = (id) => {
  const artwork = artworks.value.find(a => a.id === id)
  return artwork ? artwork.name : '-'
}

const loadData = async () => {
  loading.value = true
  try {
    plates.value = await platesApi.list(selectedArtworkId.value)
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadArtworks = async () => {
  try {
    artworks.value = await artworksApi.list()
  } catch (error) {
    console.error(error)
  }
}

const handleAdd = () => {
  if (artworks.value.length === 0) {
    message.warning('请先创建作品')
    return
  }
  isEdit.value = false
  formData.value = {
    id: null,
    artwork_id: selectedArtworkId.value || artworks.value[0]?.id,
    color_number: 1,
    ink_ratio: '',
    is_finalized: false
  }
  modalVisible.value = true
}

const handleEdit = (record) => {
  isEdit.value = true
  formData.value = { ...record }
  modalVisible.value = true
}

const handleSubmit = async () => {
  if (!formData.value.artwork_id || !formData.value.color_number) {
    message.warning('请填写必填项')
    return
  }
  submitting.value = true
  try {
    if (isEdit.value) {
      await platesApi.update(formData.value.id, formData.value)
      message.success('更新成功')
    } else {
      await platesApi.create(formData.value)
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
    await platesApi.delete(id)
    message.success('删除成功')
    loadData()
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  loadArtworks().then(() => {
    const artworkIdFromQuery = route.query.artwork_id
    if (artworkIdFromQuery) {
      selectedArtworkId.value = parseInt(artworkIdFromQuery)
    }
    loadData()
  })
})
</script>
