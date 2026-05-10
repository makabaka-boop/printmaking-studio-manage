<template>
  <div>
    <a-card title="印制批次记录">
      <a-button type="primary" @click="showAddModal" style="margin-bottom: 16px;">新建批次</a-button>
      <a-table :dataSource="batches" :columns="columns" rowKey="id" :pagination="{ pageSize: 20 }" :scroll="{ x: 1200 }">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'artwork_id'">
            {{ getArtworkName(record.artwork_id) }}
          </template>
          <template v-if="column.key === 'paper_id'">
            {{ getPaperName(record.paper_id, record.paper_name_snapshot) }}
          </template>
          <template v-if="column.key === 'plates'">
            <a-tag v-for="u in record.plate_usages" :key="u.id" color="blue">版{{ u.plate_id }}</a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-popconfirm title="确认删除此批次？" @confirm="handleDelete(record.id)">
              <a-button size="small" danger>删除</a-button>
            </a-popconfirm>
          </template>
        </template>
      </a-table>
    </a-card>

    <a-modal v-model:open="modalVisible" title="新建印制批次" @ok="handleSave" width="650px">
      <a-form :model="form" layout="vertical">
        <a-form-item label="作品" required>
          <a-select v-model:value="form.artwork_id" placeholder="选择作品" show-search optionFilterProp="label">
            <a-select-option v-for="a in artworkList" :key="a.id" :value="a.id" :label="a.name">{{ a.name }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="日期" required>
          <a-date-picker v-model:value="form.date" style="width: 100%;" valueFormat="YYYY-MM-DD" />
        </a-form-item>
        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="试印张数">
              <a-input-number v-model:value="form.trial_count" :min="0" style="width: 100%;" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="正印张数">
              <a-input-number v-model:value="form.official_count" :min="0" style="width: 100%;" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="废张数">
              <a-input-number v-model:value="form.waste_count" :min="0" style="width: 100%;" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="使用纸张" required>
          <a-select v-model:value="form.paper_id" placeholder="选择纸张">
            <a-select-option v-for="p in paperList" :key="p.id" :value="p.id">{{ p.name }} (库存:{{ p.stock }})</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="消耗纸张张数" required>
          <a-input-number v-model:value="form.paper_consumed" :min="0" style="width: 100%;" />
        </a-form-item>
        <a-form-item label="使用版次" v-if="form.artwork_id">
          <a-select v-model:value="form.plate_ids" mode="multiple" placeholder="选择使用的版次">
            <a-select-option v-for="pl in currentPlates" :key="pl.id" :value="pl.id">第{{ pl.color_order }}色版 {{ pl.is_finalized ? '(已定稿)' : '(未定稿)' }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea v-model:value="form.note" :rows="2" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../api'
import { message } from 'ant-design-vue'

const batches = ref([])
const artworkList = ref([])
const paperList = ref([])
const artworkPlates = ref({})
const modalVisible = ref(false)
const form = ref({ artwork_id: null, date: null, trial_count: 0, official_count: 0, waste_count: 0, paper_id: null, paper_consumed: 0, plate_ids: [], note: '' })

const columns = [
  { title: '作品', dataIndex: 'artwork_id', key: 'artwork_id', width: 140 },
  { title: '日期', dataIndex: 'date', key: 'date', width: 110 },
  { title: '试印', dataIndex: 'trial_count', key: 'trial_count', width: 70 },
  { title: '正印', dataIndex: 'official_count', key: 'official_count', width: 70 },
  { title: '废张', dataIndex: 'waste_count', key: 'waste_count', width: 70 },
  { title: '纸张', dataIndex: 'paper_id', key: 'paper_id', width: 120 },
  { title: '消耗纸张', dataIndex: 'paper_consumed', key: 'paper_consumed', width: 100 },
  { title: '使用版次', key: 'plates', width: 160 },
  { title: '备注', dataIndex: 'note', key: 'note', ellipsis: true },
  { title: '操作', key: 'action', width: 80, fixed: 'right' },
]

const currentPlates = computed(() => {
  if (!form.value.artwork_id) return []
  return artworkPlates.value[form.value.artwork_id] || []
})

watch(() => form.value.artwork_id, async (val) => {
  if (val && !artworkPlates.value[val]) {
    const { data } = await api.get(`/artworks/${val}/plates`)
    artworkPlates.value[val] = data
  }
  form.value.plate_ids = []
})

const getArtworkName = (id) => {
  const a = artworkList.value.find(x => x.id === id)
  return a ? a.name : id
}

const getPaperName = (id, snapshot) => {
  if (snapshot) return snapshot
  const p = paperList.value.find(x => x.id === id)
  return p ? p.name : `纸张#${id}`
}

const fetchBatches = async () => {
  const { data } = await api.get('/batches/')
  batches.value = data
}

const fetchArtworks = async () => {
  const { data } = await api.get('/artworks/')
  artworkList.value = data
}

const fetchPapers = async () => {
  const { data } = await api.get('/papers/')
  paperList.value = data
}

const showAddModal = () => {
  form.value = { artwork_id: null, date: null, trial_count: 0, official_count: 0, waste_count: 0, paper_id: null, paper_consumed: 0, plate_ids: [], note: '' }
  modalVisible.value = true
}

const handleSave = async () => {
  try {
    await api.post('/batches/', form.value)
    message.success('批次创建成功，库存已自动更新')
    modalVisible.value = false
    fetchBatches()
    fetchPapers()
    fetchArtworks()
  } catch (e) {
    message.error(e.response?.data?.detail || '创建失败')
  }
}

const handleDelete = async (id) => {
  await api.delete(`/batches/${id}`)
  message.success('删除成功')
  fetchBatches()
}

onMounted(() => {
  fetchBatches()
  fetchArtworks()
  fetchPapers()
})
</script>
