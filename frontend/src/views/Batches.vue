<template>
  <div>
    <a-page-header title="印制批次" style="margin-bottom: 24px">
      <template #extra>
        <a-button type="primary" @click="handleAdd">
          <plus-outlined />
          新建批次
        </a-button>
      </template>
    </a-page-header>

    <a-table :columns="columns" :data-source="batches" :loading="loading" row-key="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'plates'">
          <a-tag v-for="plate in record.plates" :key="plate.id" style="margin-right: 4px">
            第{{ plate.color_number }}色
          </a-tag>
        </template>
        <template v-else-if="column.key === 'waste_rate'">
          <a-progress :percent="record.waste_rate" size="small" :show-info="true" />
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
      :title="isEdit ? '编辑批次' : '新建批次'"
      @ok="handleSubmit"
      @cancel="modalVisible = false"
      :confirm-loading="submitting"
      :width="700"
    >
      <a-form :model="formData" :label-col="{ span: 4 }" :wrapper-col="{ span: 18 }">
        <a-form-item label="作品" required>
          <a-select v-model:value="formData.artwork_id" placeholder="请选择作品" @change="onArtworkChange">
            <a-select-option v-for="artwork in artworks" :key="artwork.id" :value="artwork.id">
              {{ artwork.name }} (剩余: {{ artwork.remaining_edition }})
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="印制日期" required>
          <a-date-picker v-model:value="formData.print_date" style="width: 100%" />
        </a-form-item>
        <a-form-item label="使用版次">
          <a-select v-model:value="formData.plates" mode="multiple" placeholder="请选择使用的版次" style="width: 100%">
            <a-select-option v-for="plate in availablePlates" :key="plate.id" :value="plate.id">
              第{{ plate.color_number }}色 {{ plate.is_finalized ? '(已定稿)' : '' }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="试印张数">
              <a-input-number v-model:value="formData.test_prints" :min="0" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="正印张数">
              <a-input-number v-model:value="formData.good_prints" :min="0" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="废张数">
              <a-input-number v-model:value="formData.waste_prints" :min="0" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="使用纸张">
              <a-select v-model:value="formData.paper_id" placeholder="请选择纸张" allow-clear style="width: 100%">
                <a-select-option v-for="paper in papers" :key="paper.id" :value="paper.id">
                  {{ paper.name }} (库存: {{ paper.stock }})
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="纸张用量">
              <a-input-number v-model:value="formData.paper_used" :min="0" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="备注">
          <a-textarea v-model:value="formData.notes" :rows="2" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import { batchesApi, artworksApi, platesApi, papersApi } from '@/api'

const batches = ref([])
const artworks = ref([])
const papers = ref([])
const allPlates = ref([])
const availablePlates = ref([])
const loading = ref(false)
const modalVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formData = ref({
  id: null,
  artwork_id: null,
  print_date: dayjs(),
  test_prints: 0,
  good_prints: 0,
  waste_prints: 0,
  paper_id: null,
  paper_used: 0,
  notes: '',
  plates: []
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '作品', dataIndex: 'artwork_name', key: 'artwork_name' },
  { title: '印制日期', dataIndex: 'print_date', key: 'print_date', customRender: ({ record }) => dayjs(record.print_date).format('YYYY-MM-DD') },
  { title: '使用版次', dataIndex: 'plates', key: 'plates' },
  { title: '试印', dataIndex: 'test_prints', key: 'test_prints' },
  { title: '正印', dataIndex: 'good_prints', key: 'good_prints' },
  { title: '废张', dataIndex: 'waste_prints', key: 'waste_prints' },
  { title: '废张率', dataIndex: 'waste_rate', key: 'waste_rate', width: 120 },
  { title: '纸张', dataIndex: 'paper_name', key: 'paper_name' },
  { title: '用量', dataIndex: 'paper_used', key: 'paper_used' },
  { title: '操作', key: 'action', width: 150, fixed: 'right' }
]

const loadData = async () => {
  loading.value = true
  try {
    batches.value = await batchesApi.list()
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

const loadPapers = async () => {
  try {
    papers.value = await papersApi.list()
  } catch (error) {
    console.error(error)
  }
}

const loadPlates = async () => {
  try {
    allPlates.value = await platesApi.list()
  } catch (error) {
    console.error(error)
  }
}

const onArtworkChange = (artworkId) => {
  availablePlates.value = allPlates.value.filter(p => p.artwork_id === artworkId)
}

const handleAdd = () => {
  if (artworks.value.length === 0) {
    message.warning('请先创建作品')
    return
  }
  isEdit.value = false
  formData.value = {
    id: null,
    artwork_id: artworks.value[0]?.id,
    print_date: dayjs(),
    test_prints: 0,
    good_prints: 0,
    waste_prints: 0,
    paper_id: null,
    paper_used: 0,
    notes: '',
    plates: []
  }
  onArtworkChange(formData.value.artwork_id)
  modalVisible.value = true
}

const handleEdit = (record) => {
  isEdit.value = true
  formData.value = {
    ...record,
    print_date: dayjs(record.print_date),
    plates: record.plates.map(p => p.id)
  }
  onArtworkChange(record.artwork_id)
  modalVisible.value = true
}

const handleSubmit = async () => {
  if (!formData.value.artwork_id || !formData.value.print_date) {
    message.warning('请填写必填项')
    return
  }
  submitting.value = true
  try {
    const submitData = {
      ...formData.value,
      print_date: formData.value.print_date.toISOString()
    }
    if (isEdit.value) {
      await batchesApi.update(formData.value.id, submitData)
      message.success('更新成功')
    } else {
      await batchesApi.create(submitData)
      message.success('创建成功')
    }
    modalVisible.value = false
    loadData()
    loadPapers()
    loadArtworks()
  } catch (error) {
    console.error(error)
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await batchesApi.delete(id)
    message.success('删除成功')
    loadData()
    loadPapers()
    loadArtworks()
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  loadData()
  loadArtworks()
  loadPapers()
  loadPlates()
})
</script>
