<template>
  <div>
    <a-row :gutter="16" style="margin-bottom: 24px">
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="作品总数"
            :value="stats.total_artworks"
            :value-style="{ color: '#3f8600' }"
          />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="印制批次"
            :value="stats.total_batches"
            :value-style="{ color: '#1890ff' }"
          />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="纸张种类"
            :value="stats.total_papers"
            :value-style="{ color: '#722ed1' }"
          />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="库存预警"
            :value="stats.low_stock_count"
            :value-style="{ color: '#cf1322' }"
          />
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="16">
      <a-col :span="12">
        <a-card title="各版种作品数">
          <div ref="printTypeChart" style="height: 350px"></div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="近三个月印制批次">
          <div ref="monthlyChart" style="height: 350px"></div>
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="16" style="margin-top: 16px">
      <a-col :span="12">
        <a-card title="废张率排行">
          <div ref="wasteRateChart" style="height: 350px"></div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="库存不足预警">
          <a-table
            :columns="warningColumns"
            :data-source="lowStockPapers"
            :pagination="false"
            size="small"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'status'">
                <a-tag color="red">库存不足</a-tag>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import api from '../api'

const stats = ref({
  total_artworks: 0,
  total_batches: 0,
  total_papers: 0,
  low_stock_count: 0
})

const lowStockPapers = ref([])
const printTypeChart = ref(null)
const monthlyChart = ref(null)
const wasteRateChart = ref(null)

const warningColumns = [
  { title: '纸张名称', dataIndex: 'name', key: 'name' },
  { title: '当前库存', dataIndex: 'stock_count', key: 'stock_count' },
  { title: '阈值', dataIndex: 'threshold', key: 'threshold' },
  { title: '状态', key: 'status' }
]

const loadData = async () => {
  try {
    const [statsRes, printTypesRes, monthlyRes, wasteRes, lowStockRes] = await Promise.all([
      api.getDashboardStats(),
      api.getPrintTypes(),
      api.getMonthlyBatches(),
      api.getWasteRates(),
      api.getLowStockPapers()
    ])

    stats.value = statsRes.data
    lowStockPapers.value = lowStockRes.data

    await nextTick()
    
    renderPrintTypeChart(printTypesRes.data)
    renderMonthlyChart(monthlyRes.data)
    renderWasteRateChart(wasteRes.data)
  } catch (error) {
    console.error('加载数据失败', error)
  }
}

const renderPrintTypeChart = (data) => {
  const chart = echarts.init(printTypeChart.value)
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: '5%' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 16, fontWeight: 'bold' }
      },
      data: data
    }]
  })
}

const renderMonthlyChart = (data) => {
  const chart = echarts.init(monthlyChart.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: data.map(d => d.month)
    },
    yAxis: { type: 'value' },
    series: [{
      data: data.map(d => d.count),
      type: 'line',
      smooth: true,
      itemStyle: { color: '#1890ff' },
      areaStyle: { color: 'rgba(24, 144, 255, 0.2)' }
    }]
  })
}

const renderWasteRateChart = (data) => {
  const chart = echarts.init(wasteRateChart.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value', name: '废张率(%)' },
    yAxis: {
      type: 'category',
      data: data.map(d => d.artwork_name).reverse()
    },
    series: [{
      data: data.map(d => d.waste_rate).reverse(),
      type: 'bar',
      itemStyle: {
        color: function(params) {
          return params.value > 20 ? '#ff4d4f' : '#faad14'
        }
      }
    }]
  })
}

onMounted(() => {
  loadData()
})
</script>
