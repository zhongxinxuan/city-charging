<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { FullScreen } from '@element-plus/icons-vue'
import {
  getStationsByCityChart,
  getOperatorShareChart,
  getPaymentMethodDistributionChart,
  getRecordsByCityChart,
  getAvgCostByCityChart,
  getAvgEnergyByCityChart,
  type ChartPoint,
} from '../api/charts'
import { getCities, type City } from '../api/cities'
import { getOperators, type Operator } from '../api/operators'
import { getChargerSpecs, type ChargerSpec } from '../api/chargerSpecs'
import { getStations, type StationListItem } from '../api/stations'
import { getRecords, type RecordListItem } from '../api/records'

const loading = ref(true)
const stationCount = ref(0)
const recordCount = ref(0)

const cities = ref<City[]>([])
const operators = ref<Operator[]>([])
const specs = ref<ChargerSpec[]>([])
const stationSamples = ref<StationListItem[]>([])
const recordSamples = ref<RecordListItem[]>([])

const domC1 = ref<HTMLDivElement | null>(null)
const domC2 = ref<HTMLDivElement | null>(null)
const domC3 = ref<HTMLDivElement | null>(null)
const domC4 = ref<HTMLDivElement | null>(null)
const domC5 = ref<HTMLDivElement | null>(null)
const domC6 = ref<HTMLDivElement | null>(null)

const zoomVisible = ref(false)
const zoomTitle = ref('')
const zoomChartRef = ref<HTMLDivElement | null>(null)
let zoomChart: echarts.ECharts | null = null

const chartData = {
  c1: ref<ChartPoint[]>([]),
  c2: ref<ChartPoint[]>([]),
  c3: ref<ChartPoint[]>([]),
  c4: ref<ChartPoint[]>([]),
  c5: ref<ChartPoint[]>([]),
  c6: ref<ChartPoint[]>([]),
}

const chartTitles: Record<string, string> = {
  c1: '各区县站点数量', c2: '运营商站点占比', c3: '支付方式分布',
  c4: '充电记录-按区县分布', c5: '平均充电费用-按区县', c6: '平均充电电量-按区县',
}

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444', '#ec4899', '#14b8a6', '#f97316']

onMounted(async () => {
  await loadAllData()
  window.addEventListener('resize', resizeAll)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeAll)
  charts.forEach((c) => c?.dispose())
  zoomChart?.dispose()
})

const charts: (echarts.ECharts | null)[] = []

async function loadAllData() {
  loading.value = true
  const results = await Promise.all([
    getCities().catch(() => [] as City[]),
    getOperators().catch(() => [] as Operator[]),
    getChargerSpecs().catch(() => [] as ChargerSpec[]),
    getStationsByCityChart().catch(() => [] as ChartPoint[]),
    getOperatorShareChart().catch(() => [] as ChartPoint[]),
    getPaymentMethodDistributionChart().catch(() => [] as ChartPoint[]),
    getRecordsByCityChart().catch(() => [] as ChartPoint[]),
    getAvgCostByCityChart().catch(() => [] as ChartPoint[]),
    getAvgEnergyByCityChart().catch(() => [] as ChartPoint[]),
    getStations({}).then((d) => { stationCount.value = d.length; return d }).catch(() => [] as StationListItem[]),
    getRecords({}).then((d) => { recordCount.value = d.length; return d }).catch(() => [] as RecordListItem[]),
  ])

  cities.value = results[0]; operators.value = results[1]; specs.value = results[2]
  stationSamples.value = results[9]; recordSamples.value = results[10]

  const keys = ['c1', 'c2', 'c3', 'c4', 'c5', 'c6']
  keys.forEach((k, i) => { chartData[k as keyof typeof chartData].value = results[i + 3] })

  await nextTick()
  charts.forEach((c) => c?.dispose()); charts.length = 0

  const pairs: [typeof domC1, string][] = [
    [domC1, 'c1'], [domC2, 'c2'], [domC3, 'c3'],
    [domC4, 'c4'], [domC5, 'c5'], [domC6, 'c6'],
  ]
  pairs.forEach(([domRef, key]) => {
    const el = domRef.value; const data = chartData[key as keyof typeof chartData].value
    if (!el || !data.length) { charts.push(null); return }
    const inst = echarts.init(el)
    charts.push(inst)
    inst.setOption(buildOption(key, data, false))
  })
  loading.value = false
}

function buildOption(key: string, data: ChartPoint[], zoom: boolean): echarts.EChartsOption {
  const base = (left: number, right: number, top: number, bottom: number) =>
    zoom ? { left: left * 1.3, right: right * 1.3, top: top * 1.3, bottom: bottom * 1.3 } : { left, right, top, bottom }
  const fs = zoom ? 13 : 11
  const lfs = zoom ? 14 : 11

  if (['c1', 'c4'].includes(key)) {
    return {
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: base(50, 20, 20, 50),
      xAxis: { type: 'category', data: data.map((d) => d.name), axisLabel: { rotate: 25, fontSize: fs, color: '#94a3b8' }, axisLine: { show: false }, axisTick: { show: false } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }, axisLabel: { fontSize: fs, color: '#94a3b8' } },
      series: [{ type: 'bar', barWidth: '60%', data: data.map((d, i) => ({ value: d.value, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: COLORS[i % COLORS.length] }, { offset: 1, color: COLORS[i % COLORS.length] + '55' }]), borderRadius: [4, 4, 0, 0] } })), label: { show: true, position: 'top', fontSize: lfs, fontWeight: 600, color: '#64748b', formatter: (p: { value: number }) => p.value } }],
    }
  }
  if (key === 'c2') {
    return {
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: 0, textStyle: { fontSize: fs, color: '#64748b' } },
      series: [{ type: 'pie', radius: zoom ? ['30%', '62%'] : ['35%', '65%'], center: ['50%', '42%'], label: zoom ? { show: true, formatter: '{b}', fontSize: 12 } : { show: false }, emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } }, data: data.map((item, i) => ({ ...item, itemStyle: { color: COLORS[i % COLORS.length] } })) }],
    }
  }
  if (key === 'c3') {
    const colorMap: Record<string, string> = { '微信支付': '#07c160', '支付宝': '#1677ff', '信用卡': '#f59e0b', '现金': '#8b5cf6' }
    return {
      tooltip: { trigger: 'item', formatter: '{b}: {c} 笔 ({d}%)' },
      legend: { bottom: 0, textStyle: { fontSize: fs, color: '#64748b' } },
      series: [{ type: 'pie', radius: ['30%', '62%'], center: ['50%', '42%'], label: { show: true, formatter: '{b}', fontSize: zoom ? 12 : 10 }, data: data.map((item) => ({ ...item, itemStyle: { color: colorMap[item.name] || '#94a3b8' } })) }],
    }
  }
  const suffix = key === 'c5' ? '元' : 'kWh'
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (p: { name: string; value: number }[]) => `<strong>${p[0].name}</strong><br/>${suffix}: <strong>${p[0].value} ${suffix}</strong>` },
    grid: base(50, 20, 20, 50),
    xAxis: { type: 'category', data: data.map((d) => d.name), axisLabel: { rotate: 25, fontSize: fs, color: '#94a3b8' }, axisLine: { show: false }, axisTick: { show: false } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }, axisLabel: { fontSize: fs, color: '#94a3b8' } },
    series: [{ type: 'bar', barWidth: '55%', data: data.map((d, i) => ({ value: d.value, itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: COLORS[(i + 3) % COLORS.length] }, { offset: 1, color: COLORS[(i + 3) % COLORS.length] + '55' }]), borderRadius: [4, 4, 0, 0] } })), label: { show: true, position: 'top', fontSize: lfs, fontWeight: 600, color: '#64748b', formatter: (p: { value: number }) => p.value + suffix } }],
  }
}

let pendingZoomKey = ''

function openZoom(key: string) {
  zoomTitle.value = chartTitles[key]
  pendingZoomKey = key
  zoomVisible.value = true
}

function handleZoomOpened() {
  if (!zoomChartRef.value || !pendingZoomKey) return
  zoomChart?.dispose()
  const el = zoomChartRef.value
  el.style.width = '100%'
  el.style.height = '68vh'
  zoomChart = echarts.init(el)
  const data = chartData[pendingZoomKey as keyof typeof chartData].value
  if (!data.length) return
  setTimeout(() => {
    zoomChart!.setOption(buildOption(pendingZoomKey, data, true))
    zoomChart!.resize()
  }, 200)
}

function closeZoom() { zoomVisible.value = false; zoomChart?.dispose(); zoomChart = null }

function resizeAll() { charts.forEach((c) => c?.resize()); zoomChart?.resize() }

function formatDateTime(value: string | null) { if (!value) return '-'; return value.replace('T', ' ') }
function displayValue(value: string | number | boolean | null | undefined, suffix = '') { if (value === null || value === undefined || value === '') return '-'; return `${value}${suffix}` }
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h2>数据总览</h2>
      <p>充电桩系统全维度数据聚合展示与统计分析</p>
    </div>

    <div v-loading="loading" class="overview-content">
      <el-row :gutter="16" class="stat-row">
        <el-col :xs="12" :sm="6"><el-card shadow="never" class="stat-mini"><span class="label">充电站</span><span class="num">{{ stationCount }}</span></el-card></el-col>
        <el-col :xs="12" :sm="6"><el-card shadow="never" class="stat-mini"><span class="label">充电记录</span><span class="num">{{ recordCount }}</span></el-card></el-col>
        <el-col :xs="12" :sm="6"><el-card shadow="never" class="stat-mini"><span class="label">城市/区县</span><span class="num">{{ cities.length }}</span></el-card></el-col>
        <el-col :xs="12" :sm="6"><el-card shadow="never" class="stat-mini"><span class="label">运营商</span><span class="num">{{ operators.length }}</span></el-card></el-col>
      </el-row>

      <el-row :gutter="16" class="chart-row">
        <el-col :xs="24" :md="8"><el-card shadow="never" class="chart-card-lg"><template #header><div class="card-header-row"><strong>各区县站点数量</strong><el-button size="small" circle :icon="FullScreen" class="zoom-btn" @click="openZoom('c1')" /></div></template><div ref="domC1" class="chart-box-lg"></div></el-card></el-col>
        <el-col :xs="24" :md="8"><el-card shadow="never" class="chart-card-lg"><template #header><div class="card-header-row"><strong>运营商站点占比</strong><el-button size="small" circle :icon="FullScreen" class="zoom-btn" @click="openZoom('c2')" /></div></template><div ref="domC2" class="chart-box-lg"></div></el-card></el-col>
        <el-col :xs="24" :md="8"><el-card shadow="never" class="chart-card-lg"><template #header><div class="card-header-row"><strong>支付方式分布</strong><el-button size="small" circle :icon="FullScreen" class="zoom-btn" @click="openZoom('c3')" /></div></template><div ref="domC3" class="chart-box-lg"></div></el-card></el-col>
      </el-row>

      <el-row :gutter="16" class="chart-row">
        <el-col :xs="24" :md="8"><el-card shadow="never" class="chart-card-lg"><template #header><div class="card-header-row"><strong>充电记录-按区县分布</strong><el-button size="small" circle :icon="FullScreen" class="zoom-btn" @click="openZoom('c4')" /></div></template><div ref="domC4" class="chart-box-lg"></div></el-card></el-col>
        <el-col :xs="24" :md="8"><el-card shadow="never" class="chart-card-lg"><template #header><div class="card-header-row"><strong>平均充电费用-按区县</strong><el-button size="small" circle :icon="FullScreen" class="zoom-btn" @click="openZoom('c5')" /></div></template><div ref="domC5" class="chart-box-lg"></div></el-card></el-col>
        <el-col :xs="24" :md="8"><el-card shadow="never" class="chart-card-lg"><template #header><div class="card-header-row"><strong>平均充电电量-按区县</strong><el-button size="small" circle :icon="FullScreen" class="zoom-btn" @click="openZoom('c6')" /></div></template><div ref="domC6" class="chart-box-lg"></div></el-card></el-col>
      </el-row>

      <el-row :gutter="16" class="chart-row">
        <el-col :xs="24" :md="12"><el-card shadow="never" class="data-card"><template #header><div class="card-header-row"><strong>运营商信息</strong><el-tag size="small">{{ operators.length }} 家</el-tag></div></template><el-table :data="operators" size="small" border stripe><el-table-column prop="operator_name" label="运营商名称" /><el-table-column prop="company_type" label="类型" width="100" /><el-table-column prop="founded_year" label="成立年份" width="100" /><el-table-column prop="headquarters" label="总部" width="120" show-overflow-tooltip /></el-table></el-card></el-col>
        <el-col :xs="24" :md="12"><el-card shadow="never" class="data-card"><template #header><div class="card-header-row"><strong>充电桩规格</strong><el-tag size="small">{{ specs.length }} 种</el-tag></div></template><el-table :data="specs" size="small" border stripe><el-table-column prop="type_name" label="类型" /><el-table-column label="功率" width="80"><template #default="{ row }">{{ displayValue(row.power_kw, 'kW') }}</template></el-table-column><el-table-column label="电压" width="75"><template #default="{ row }">{{ displayValue(row.voltage_v, 'V') }}</template></el-table-column><el-table-column prop="connector_type" label="接口" width="90" /><el-table-column label="价格" width="85"><template #default="{ row }">{{ displayValue(row.cost_per_kwh, '元/kWh') }}</template></el-table-column></el-table></el-card></el-col>
      </el-row>

      <el-row :gutter="16" class="chart-row">
        <el-col :xs="24" :md="12"><el-card shadow="never" class="data-card"><template #header><div class="card-header-row"><strong>充电站样本数据</strong><el-tag size="small">前 {{ stationSamples.length }} 条</el-tag></div></template><el-table :data="stationSamples" size="small" border stripe max-height="320"><el-table-column prop="station_name" label="站点名称" min-width="200" show-overflow-tooltip /><el-table-column prop="city_name" label="城市" width="100" /><el-table-column prop="operator_name" label="运营商" width="130" /><el-table-column prop="type_name" label="类型" width="120" /><el-table-column label="功率" width="100"><template #default="{ row }">{{ displayValue(row.power_kw, ' kW') }}</template></el-table-column></el-table></el-card></el-col>
        <el-col :xs="24" :md="12"><el-card shadow="never" class="data-card"><template #header><div class="card-header-row"><strong>充电记录样本数据</strong><el-tag size="small">前 {{ recordSamples.length }} 条</el-tag></div></template><el-table :data="recordSamples" size="small" border stripe max-height="320"><el-table-column prop="record_id" label="编号" width="130" /><el-table-column prop="username" label="用户" width="80" /><el-table-column prop="station_name" label="站点" min-width="150" show-overflow-tooltip /><el-table-column label="开始时间" width="150"><template #default="{ row }">{{ formatDateTime(row.charge_start_time) }}</template></el-table-column><el-table-column label="电量" width="90"><template #default="{ row }">{{ displayValue(row.energy_kwh, ' kWh') }}</template></el-table-column><el-table-column label="费用" width="90"><template #default="{ row }">{{ displayValue(row.cost_yuan, ' 元') }}</template></el-table-column></el-table></el-card></el-col>
      </el-row>
    </div>
  </div>

  <el-dialog v-model="zoomVisible" :title="zoomTitle" width="85%" top="4vh" :close-on-click-modal="false" @opened="handleZoomOpened" @closed="zoomChart?.dispose(); zoomChart = null">
    <div ref="zoomChartRef" class="zoom-chart-box"></div>
  </el-dialog>
</template>

<style scoped>
.overview-content { max-width: 1400px; }
.stat-row { margin-bottom: 16px !important; }
.stat-mini { border-radius: var(--radius-md) !important; border: 1px solid var(--border-color) !important; padding: 8px 0; }
.stat-mini .label { display: block; font-size: 12px; color: var(--text-secondary); font-weight: 600; margin-bottom: 4px; }
.stat-mini .num { display: block; font-size: 24px; font-weight: 800; color: var(--text-primary); }
.chart-row { margin-bottom: 16px !important; }
.chart-card-lg { border-radius: var(--radius-md) !important; border: 1px solid var(--border-color) !important; }
.chart-box-lg { width: 100%; height: 230px; }
.data-card { border-radius: var(--radius-md) !important; border: 1px solid var(--border-color) !important; margin-bottom: 0; }
.card-header-row { display: flex; align-items: center; justify-content: space-between; }
.zoom-btn { color: var(--text-tertiary); transition: color 0.2s; }
.zoom-btn:hover { color: var(--primary); }
:deep(.zoom-chart-box) { width: 100%; height: 68vh; }
</style>
