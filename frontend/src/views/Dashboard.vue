<template>
  <div>
    <a-row :gutter="16" style="margin-bottom: 16px;">
      <a-col :span="12">
        <a-card title="各版种作品数">
          <div ref="pieRef" style="height: 320px;"></div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="近三个月印制批次">
          <div ref="lineRef" style="height: 320px;"></div>
        </a-card>
      </a-col>
    </a-row>
    <a-row :gutter="16">
      <a-col :span="12">
        <a-card title="废张率排行">
          <div ref="barRef" style="height: 320px;"></div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="库存不足纸张预警">
          <a-table :dataSource="alerts" :columns="alertColumns" rowKey="id" size="small" :pagination="false">
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'stock'">
                <a-tag color="red">{{ record.stock }}</a-tag>
              </template>
              <template v-if="column.key === 'threshold'">
                <a-tag color="orange">{{ record.threshold }}</a-tag>
              </template>
            </template>
          </a-table>
          <a-empty v-if="alerts.length === 0" description="暂无库存预警" style="margin-top: 24px;" />
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import api from '../api'

const pieRef = ref(null)
const lineRef = ref(null)
const barRef = ref(null)
const alerts = ref([])

const alertColumns = [
  { title: '纸张名称', dataIndex: 'name', key: 'name' },
  { title: '当前库存', dataIndex: 'stock', key: 'stock' },
  { title: '告警阈值', dataIndex: 'threshold', key: 'threshold' },
]

let pieChart, lineChart, barChart

const initPie = async () => {
  const { data } = await api.get('/dashboard/pie')
  pieChart = echarts.init(pieRef.value)
  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      itemStyle: { borderRadius: 8 },
      label: { formatter: '{b}\n{c} 件' },
      data: data,
    }],
    color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
  })
}

const initLine = async () => {
  const { data } = await api.get('/dashboard/line')
  lineChart = echarts.init(lineRef.value)
  lineChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.map(d => d.month) },
    yAxis: { type: 'value', name: '批次数', minInterval: 1 },
    series: [{
      type: 'line',
      data: data.map(d => d.count),
      smooth: true,
      areaStyle: { opacity: 0.15 },
      itemStyle: { color: '#5470c6' },
    }],
  })
}

const initBar = async () => {
  const { data } = await api.get('/dashboard/waste')
  barChart = echarts.init(barRef.value)
  barChart.setOption({
    tooltip: { trigger: 'axis', formatter: (params) => `${params[0].name}<br/>废张率: ${params[0].value}%` },
    xAxis: { type: 'category', data: data.map(d => d.artwork_name), axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: '废张率(%)' },
    series: [{
      type: 'bar',
      data: data.map(d => d.waste_rate),
      itemStyle: { color: '#ee6666', borderRadius: [4, 4, 0, 0] },
    }],
  })
}

const fetchAlerts = async () => {
  const { data } = await api.get('/dashboard/alerts')
  alerts.value = data
}

onMounted(async () => {
  await nextTick()
  initPie()
  initLine()
  initBar()
  fetchAlerts()

  window.addEventListener('resize', () => {
    pieChart?.resize()
    lineChart?.resize()
    barChart?.resize()
  })
})
</script>
