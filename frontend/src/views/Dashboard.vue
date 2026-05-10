<template>
  <div>
    <a-row :gutter="16" style="margin-bottom: 24px">
      <a-col :span="6">
        <a-card>
          <a-statistic title="作品总数" :value="stats.total_artworks" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="印制批次" :value="stats.total_batches" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="纸张种类" :value="stats.total_papers" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="库存预警" :value="stats.low_stock_count" :value-style="{ color: '#ff4d4f' }" />
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="16" style="margin-bottom: 24px">
      <a-col :span="12">
        <a-card title="各版种作品数">
          <div ref="printTypeChart" style="height: 300px"></div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="近三个月印制批次">
          <div ref="recentBatchesChart" style="height: 300px"></div>
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="16">
      <a-col :span="12">
        <a-card title="废张率排行">
          <div ref="wasteRateChart" style="height: 300px"></div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="库存不足预警">
          <a-table
            :columns="lowStockColumns"
            :data-source="lowStockPapers"
            :pagination="false"
            size="small"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'stock'">
                <a-tag color="red">{{ record.stock }}</a-tag>
              </template>
              <template v-else-if="column.key === 'deficit'">
                <span style="color: #ff4d4f; font-weight: bold">-{{ record.deficit }}</span>
              </template>
            </template>
          </a-table>
          <a-empty v-if="lowStockPapers.length === 0" description="暂无库存不足的纸张" />
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { dashboardApi } from '@/api'

const stats = ref({
  total_artworks: 0,
  total_batches: 0,
  total_papers: 0,
  low_stock_count: 0
})

const lowStockPapers = ref([])
const lowStockColumns = [
  { title: '纸张名称', dataIndex: 'name', key: 'name' },
  { title: '克重/幅面', dataIndex: 'size', key: 'size', customRender: ({ record }) => `${record.weight || '-'}g / ${record.size || '-'}` },
  { title: '当前库存', dataIndex: 'stock', key: 'stock' },
  { title: '阈值', dataIndex: 'threshold', key: 'threshold' },
  { title: '缺口', dataIndex: 'deficit', key: 'deficit' }
]

const printTypeChart = ref(null)
const recentBatchesChart = ref(null)
const wasteRateChart = ref(null)

let printTypeChartInstance = null
let recentBatchesChartInstance = null
let wasteRateChartInstance = null

const loadData = async () => {
  try {
    const [statsData, printTypeData, recentBatchesData, wasteRateData, lowStockData] = await Promise.all([
      dashboardApi.stats(),
      dashboardApi.printTypeChart(),
      dashboardApi.recentBatchesChart(),
      dashboardApi.wasteRateChart(),
      dashboardApi.lowStockPapers()
    ])

    stats.value = statsData
    lowStockPapers.value = lowStockData

    initPrintTypeChart(printTypeData)
    initRecentBatchesChart(recentBatchesData)
    initWasteRateChart(wasteRateData)
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const initPrintTypeChart = (data) => {
  if (!printTypeChart.value) return
  printTypeChartInstance = echarts.init(printTypeChart.value)
  printTypeChartInstance.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: '0' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false, position: 'center' },
      emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold' } },
      labelLine: { show: false },
      data: data.length > 0 ? data : [{ name: '暂无数据', value: 1 }]
    }]
  })
}

const initRecentBatchesChart = (data) => {
  if (!recentBatchesChart.value) return
  recentBatchesChartInstance = echarts.init(recentBatchesChart.value)
  recentBatchesChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: data.dates || [] },
    yAxis: { type: 'value' },
    series: [{
      name: '批次数量',
      type: 'line',
      smooth: true,
      areaStyle: {},
      data: data.counts || []
    }]
  })
}

const initWasteRateChart = (data) => {
  if (!wasteRateChart.value) return
  wasteRateChartInstance = echarts.init(wasteRateChart.value)
  wasteRateChartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', name: '废张率(%)' },
    yAxis: { type: 'category', data: data.map(item => item.name).reverse() },
    series: [{
      type: 'bar',
      data: data.map(item => item.waste_rate).reverse(),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#83bff6' },
          { offset: 0.5, color: '#188df0' },
          { offset: 1, color: '#188df0' }
        ])
      },
      label: { show: true, position: 'right', formatter: '{c}%' }
    }]
  })
}

const handleResize = () => {
  printTypeChartInstance?.resize()
  recentBatchesChartInstance?.resize()
  wasteRateChartInstance?.resize()
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  printTypeChartInstance?.dispose()
  recentBatchesChartInstance?.dispose()
  wasteRateChartInstance?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>
