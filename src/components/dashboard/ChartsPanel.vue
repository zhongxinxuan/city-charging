<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import {
  getStationsByCityChart,
  getOperatorShareChart,
  getStationTypeDistributionChart,
  type ChartPoint,
} from '../../api/charts'
import { ElMessage } from 'element-plus'
import { FullScreen } from '@element-plus/icons-vue'

const cityChartRef = ref<HTMLDivElement | null>(null)
const operatorChartRef = ref<HTMLDivElement | null>(null)
const typeChartRef = ref<HTMLDivElement | null>(null)

let cityChart: echarts.ECharts | null = null
let operatorChart: echarts.ECharts | null = null
let typeChart: echarts.ECharts | null = null

const loading = ref(true)

const cityData = ref<ChartPoint[]>([])
const operatorData = ref<ChartPoint[]>([])
const typeData = ref<ChartPoint[]>([])

const zoomVisible = ref(false)
const zoomTitle = ref('')
const zoomChartKey = ref<'city' | 'operator' | 'type' | null>(null)
const zoomChartRef = ref<HTMLDivElement | null>(null)
let zoomChart: echarts.ECharts | null = null

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444', '#ec4899', '#14b8a6', '#f97316']

onMounted(async () => {
  await loadCharts()
  window.addEventListener('resize', resizeCharts)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts)
  cityChart?.dispose()
  operatorChart?.dispose()
  typeChart?.dispose()
  zoomChart?.dispose()
})

async function loadCharts() {
  try {
    loading.value = true
    const [cd, od, td] = await Promise.all([
      getStationsByCityChart(),
      getOperatorShareChart(),
      getStationTypeDistributionChart(),
    ])
    cityData.value = cd
    operatorData.value = od
    typeData.value = td
    await nextTick()
    renderCityChart(cd)
    renderOperatorChart(od)
    renderTypeChart(td)
  } catch {
    ElMessage.warning('图表数据加载失败，请确认后端已启动')
  } finally {
    loading.value = false
  }
}

function renderCityChart(data: ChartPoint[]) {
  if (!cityChartRef.value) return
  const total = data.reduce((s, d) => s + d.value, 0)
  cityChart?.dispose()
  cityChart = echarts.init(cityChartRef.value)
  cityChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' },
      formatter: (params: { name: string; value: number }[]) => {
        const p = params[0]; const pct = ((p.value / total) * 100).toFixed(1)
        return `<strong>${p.name}</strong><br/>站点数: <strong>${p.value}</strong> (占比 ${pct}%)`
      },
    },
    grid: { left: 50, right: 30, top: 20, bottom: 56 },
    xAxis: { type: 'category', data: data.map((d) => d.name), axisLabel: { rotate: 30, fontSize: 11, color: '#94a3b8', interval: 0 }, axisLine: { show: false }, axisTick: { show: false } },
    yAxis: { type: 'value', name: '站点数', splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }, axisLabel: { fontSize: 11, color: '#94a3b8' } },
    series: [{ type: 'bar', data: data.map((d, i) => ({ value: d.value, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: COLORS[i % COLORS.length] }, { offset: 1, color: COLORS[i % COLORS.length] + '55' }]), borderRadius: [4, 4, 0, 0] } })), barWidth: '65%', label: { show: true, position: 'top', fontSize: 11, fontWeight: 700, color: '#475569', formatter: (p: { value: number }) => p.value } }],
  })
}

function renderOperatorChart(data: ChartPoint[]) {
  if (!operatorChartRef.value) return
  operatorChart?.dispose()
  operatorChart = echarts.init(operatorChartRef.value)
  operatorChart.setOption({
    tooltip: { trigger: 'item', formatter: (p: { name: string; value: number; percent: number }) => `<strong>${p.name}</strong><br/>站点数: <strong>${p.value}</strong><br/>占比: <strong>${p.percent.toFixed(1)}%</strong>` },
    legend: { bottom: 0, type: 'scroll', textStyle: { fontSize: 11, color: '#64748b' } },
    series: [{ type: 'pie', radius: ['38%', '68%'], center: ['50%', '40%'], avoidLabelOverlap: true, label: { show: true, formatter: (p: { percent: number }) => p.percent.toFixed(0) + '%', fontSize: 11, fontWeight: 700, color: '#475569' }, emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' }, itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.15)' } }, data: data.map((item, i) => ({ ...item, itemStyle: { color: COLORS[i % COLORS.length] } })) }],
  })
}

function renderTypeChart(data: ChartPoint[]) {
  if (!typeChartRef.value) return
  typeChart?.dispose()
  typeChart = echarts.init(typeChartRef.value)
  typeChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: { name: string; value: number }[]) => `<strong>${params[0].name}</strong><br/>站点数: <strong>${params[0].value}</strong>` },
    grid: { left: 10, right: 40, top: 20, bottom: 20 },
    xAxis: { type: 'value', splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }, axisLabel: { fontSize: 11, color: '#94a3b8' } },
    yAxis: { type: 'category', data: data.map((d) => d.name).reverse(), axisLine: { show: false }, axisTick: { show: false }, axisLabel: { fontSize: 11, color: '#64748b', fontWeight: 600 } },
    series: [{ type: 'bar', data: data.map((d, i) => ({ value: d.value, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: COLORS[i % COLORS.length] + '55' }, { offset: 1, color: COLORS[i % COLORS.length] }]), borderRadius: [0, 4, 4, 0] } })).reverse(), barWidth: '55%', label: { show: true, position: 'right', fontSize: 11, fontWeight: 700, color: '#475569', formatter: (p: { value: number }) => p.value + ' 站' } }],
  })
}

let pendingZoomKey = ''

function openZoom(key: 'city' | 'operator' | 'type') {
  const titles: Record<string, string> = { city: '各区县站点数量', operator: '运营商市场占比', type: '充电桩类型分布' }
  zoomTitle.value = titles[key]
  pendingZoomKey = key
  zoomChartKey.value = key
  zoomVisible.value = true
}

function handleZoomOpened() {
  if (!zoomChartRef.value || !pendingZoomKey) return
  zoomChart?.dispose()
  const el = zoomChartRef.value
  el.style.width = '100%'
  el.style.height = '68vh'
  zoomChart = echarts.init(el)
  const dataMap: Record<string, ChartPoint[]> = { city: cityData.value, operator: operatorData.value, type: typeData.value }
  const data = dataMap[pendingZoomKey]
  if (!data || !data.length) return
  const renderChart = () => {
    if (pendingZoomKey === 'city') {
      const total = data.reduce((s, d) => s + d.value, 0)
      zoomChart!.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: { name: string; value: number }[]) => { const p = params[0]; const pct = ((p.value / total) * 100).toFixed(1); return `<strong>${p.name}</strong><br/>站点数: <strong>${p.value}</strong> (占比 ${pct}%)` } },
        grid: { left: 60, right: 40, top: 30, bottom: 60 },
        xAxis: { type: 'category', data: data.map((d) => d.name), axisLabel: { rotate: 30, fontSize: 13, color: '#94a3b8' }, axisLine: { show: false }, axisTick: { show: false } },
        yAxis: { type: 'value', name: '站点数', splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }, axisLabel: { fontSize: 13, color: '#94a3b8' } },
        series: [{ type: 'bar', data: data.map((d, i) => ({ value: d.value, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: COLORS[i % COLORS.length] }, { offset: 1, color: COLORS[i % COLORS.length] + '55' }]), borderRadius: [4, 4, 0, 0] } })), barWidth: '60%', label: { show: true, position: 'top', fontSize: 13, fontWeight: 700, color: '#475569', formatter: (p: { value: number }) => p.value } }],
      })
    } else if (pendingZoomKey === 'operator') {
      zoomChart!.setOption({
        tooltip: { trigger: 'item', formatter: (p: { name: string; value: number; percent: number }) => `<strong>${p.name}</strong><br/>站点数: <strong>${p.value}</strong><br/>占比: <strong>${p.percent.toFixed(1)}%</strong>` },
        legend: { bottom: 0, type: 'scroll', textStyle: { fontSize: 13, color: '#64748b' } },
        series: [{ type: 'pie', radius: ['35%', '65%'], center: ['50%', '42%'], avoidLabelOverlap: true, label: { show: true, formatter: (p: { percent: number }) => p.percent.toFixed(0) + '%', fontSize: 13, fontWeight: 700, color: '#475569' }, emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' }, itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.15)' } }, data: data.map((item, i) => ({ ...item, itemStyle: { color: COLORS[i % COLORS.length] } })) }],
      })
    } else {
      zoomChart!.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: { name: string; value: number }[]) => `<strong>${params[0].name}</strong><br/>站点数: <strong>${params[0].value}</strong>` },
        grid: { left: 20, right: 60, top: 30, bottom: 30 },
        xAxis: { type: 'value', splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }, axisLabel: { fontSize: 13, color: '#94a3b8' } },
        yAxis: { type: 'category', data: data.map((d) => d.name).reverse(), axisLine: { show: false }, axisTick: { show: false }, axisLabel: { fontSize: 13, color: '#64748b', fontWeight: 600 } },
        series: [{ type: 'bar', data: data.map((d, i) => ({ value: d.value, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: COLORS[i % COLORS.length] + '55' }, { offset: 1, color: COLORS[i % COLORS.length] }]), borderRadius: [0, 4, 4, 0] } })).reverse(), barWidth: '50%', label: { show: true, position: 'right', fontSize: 13, fontWeight: 700, color: '#475569', formatter: (p: { value: number }) => p.value + ' 站' } }],
      })
    }
    zoomChart!.resize()
  }
  setTimeout(renderChart, 200)
}

function closeZoom() {
  zoomVisible.value = false
  zoomChart?.dispose()
  zoomChart = null
}

function resizeCharts() {
  cityChart?.resize()
  operatorChart?.resize()
  typeChart?.resize()
  zoomChart?.resize()
}

function refresh() { loadCharts() }
defineExpose({ refresh })
</script>

<template>
  <div class="chart-section">
    <div class="overview-header">
      <div>
        <h2>统计看板</h2>
        <span>基于 ECharts 的数据可视化详细展示</span>
      </div>
      <el-button size="small" @click="refresh" :loading="loading">
        <el-icon><Refresh /></el-icon> 刷新
      </el-button>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="24" :md="8" class="chart-col">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="chart-card-header">
              <strong>各区县站点数量</strong>
              <div class="chart-header-right">
                <el-tag size="small" effect="plain" color="#d1fae5">柱状图</el-tag>
                <el-button size="small" circle :icon="FullScreen" class="zoom-btn" @click="openZoom('city')" />
              </div>
            </div>
          </template>
          <div ref="cityChartRef" class="chart-box" v-loading="loading"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="8" class="chart-col">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="chart-card-header">
              <strong>运营商市场占比</strong>
              <div class="chart-header-right">
                <el-tag size="small" effect="plain" color="#dbeafe">环形饼图</el-tag>
                <el-button size="small" circle :icon="FullScreen" class="zoom-btn" @click="openZoom('operator')" />
              </div>
            </div>
          </template>
          <div ref="operatorChartRef" class="chart-box" v-loading="loading"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="8" class="chart-col">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="chart-card-header">
              <strong>充电桩类型分布</strong>
              <div class="chart-header-right">
                <el-tag size="small" effect="plain" color="#fef3c7">横向柱状图</el-tag>
                <el-button size="small" circle :icon="FullScreen" class="zoom-btn" @click="openZoom('type')" />
              </div>
            </div>
          </template>
          <div ref="typeChartRef" class="chart-box" v-loading="loading"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>

  <el-dialog v-model="zoomVisible" :title="zoomTitle" width="85%" top="4vh" :close-on-click-modal="false" @opened="handleZoomOpened" @closed="zoomChart?.dispose(); zoomChart = null">
    <div ref="zoomChartRef" class="zoom-chart-box"></div>
  </el-dialog>
</template>

<style scoped>
.chart-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
}
.chart-col { margin-bottom: 0; }
.chart-card { border: 1px solid var(--border-light) !important; border-radius: var(--radius-sm) !important; }
.chart-card-header { display: flex; align-items: center; justify-content: space-between; }
.chart-header-right { display: flex; align-items: center; gap: 6px; }
.chart-card-header strong { font-size: 14px; color: var(--text-primary); }
.chart-box { width: 100%; height: 230px; }
.zoom-btn { color: var(--text-tertiary); transition: color 0.2s; }
.zoom-btn:hover { color: var(--primary); }
.overview-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.overview-header h2 { font-size: 18px; font-weight: 700; margin: 0; color: var(--text-primary); }
.overview-header span { color: var(--text-tertiary); font-size: 12px; }
:deep(.zoom-chart-box) { width: 100%; height: 68vh; }
</style>
