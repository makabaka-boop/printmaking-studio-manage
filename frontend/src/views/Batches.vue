<template>
  <a-card title="印制批次记录">
    <template #extra>
      <a-button type="primary" @click="showModal = true">
        <PlusOutlined /> 新增批次
      </a-button>
    </template>

    <a-table :columns="columns" :data-source="batches" row-key="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'artwork_name'">
          {{ getArtworkName(record.artwork_id) }}
        </template>
        <template v-else-if="column.key === 'paper_name'">
          {{ getPaperName(record.paper_id) }}
        </template>
        <template v-else-if="column.key === 'action'">
          <a-popconfirm title="确定删除? 删除将回滚库存和版数" @confirm="handleDelete(record.id)">
            <a-button type="link" danger>删除</a-button>
          </a-popconfirm>
        </template>
      </template>
    </a-table>

    <a-modal
      v-model:open="showModal"
      title="新增印制批次"
      @ok="handleSubmit"
      :confirm-loading="loading"
      width="600px"
    >
      <a-form :model="form" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="作品" required>
              <a-select v-model:value="form.artwork_id" placeholder="请选择作品">
                <a-select-option v-for="a in artworks" :key="a.id" :value="a.id">
                  {{ a.name }} (剩余: {{ a.remaining_edition }})
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="印制日期" required>
              <a-date-picker v-model:value="form.print_date" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="使用版次">
          <a-input v-model:value="form.plate_ids" placeholder="如：1,2,3" />
        </a-form-item>
        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="试印张数">
              <a-input-number v-model:value="form.trial_print_count" :min="0" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="正印张数">
              <a-input-number v-model:value="form.final_print_count" :min="0" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="废张数">
              <a-input-number v-model:value="form.waste_count" :min="0" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="使用纸张">
              <a-select v-model:value="form.paper_id" placeholder="请选择纸张">
                <a-select-option v-for="p in papers" :key="p.id" :value="p.id">
                  {{ p.name }} (库存: {{ p.stock_count }})
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="消耗张数">
              <a-input-number v-model:value="form.paper_used" :min="0" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
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
import dayjs from 'dayjs'
import api from '../api'

const batches = ref([])
const artworks = ref([])
const papers = ref([])
const showModal = ref(false)
const loading = ref(false)
const form = ref({
  artwork_id: null,
  print_date: dayjs(),
  plate_ids: '',
  trial_print_count: 0,
  final_print_count: 0,
  waste_count: 0,
  paper_id: null,
  paper_used: 0,
  notes: ''
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '作品', key: 'artwork_name' },
  { title: '日期', dataIndex: 'print_date', key: 'print_date' },
  { title: '使用版次', dataIndex: 'plate_ids', key: 'plate_ids' },
  { title: '试印', dataIndex: 'trial_print_count', key: 'trial_print_count', width: 80 },
  { title: '正印', dataIndex: 'final_print_count', key: 'final_print_count', width: 80 },
  { title: '废张', dataIndex: 'waste_count', key: 'waste_count', width: 80 },
  { title: '纸张', key: 'paper_name' },
  { title: '消耗', dataIndex: 'paper_used', key: 'paper_used', width: 80 },
  { title: '操作', key: 'action', width: 100 }
]

const loadData = async () => {
  const [batchesRes, artworksRes, papersRes] = await Promise.all([
    api.getBatches(),
    api.getArtworks(),
    api.getPapers()
  ])
  batches.value = batchesRes.data
  artworks.value = artworksRes.data
  papers.value = papersRes.data
}

const getArtworkName = (id) => {
  const a = artworks.value.find(x => x.id === id)
  return a ? a.name : '-'
}

const getPaperName = (id) => {
  const p = papers.value.find(x => x.id === id)
  return p ? p.name : '-'
}

const handleSubmit = async () => {
  if (!form.value.artwork_id || !form.value.print_date) {
    message.warning('请填写必填项')
    return
  }
  loading.value = true
  try {
    const data = {
      ...form.value,
      print_date: form.value.print_date.format('YYYY-MM-DD')
    }
    await api.createBatch(data)
    message.success('创建成功，库存已更新')
    showModal.value = false
    form.value = {
      artwork_id: null,
      print_date: dayjs(),
      plate_ids: '',
      trial_print_count: 0,
      final_print_count: 0,
      waste_count: 0,
      paper_id: null,
      paper_used: 0,
      notes: ''
    }
    loadData()
  } catch (error) {
    message.error('创建失败')
  } finally {
    loading.value = false
  }
}

const handleDelete = async (id) => {
  await api.deleteBatch(id)
  message.success('删除成功，库存已回滚')
  loadData()
}

onMounted(() => {
  loadData()
})
</script>
