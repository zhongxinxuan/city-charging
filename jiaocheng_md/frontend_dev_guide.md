# 前端开发教程

本文档说明"城市充电桩信息查询系统"前端项目的开发流程。前端使用 Vue 3 + TypeScript + Element Plus + ECharts 技术栈，采用组件化开发方式。

## 1. 前端在系统中的作用

整体数据流：

```text
Vue 前端页面
    │
    ▼ 点击按钮
Axios HTTP 请求
    │
    ▼
FastAPI 后端接口
    │
    ▼
PostgreSQL 数据库
    │
    ▼ 返回 JSON
前端渲染到界面
```

前端不直接连接数据库，而是通过 HTTP 请求调用后端的 RESTful API。

## 2. 前端项目结构

```text
src/
├── api/                 API 请求模块
│   ├── http.ts          Axios 实例
│   ├── cities.ts        城市接口
│   ├── operators.ts     运营商接口
│   ├── chargerSpecs.ts  充电桩规格接口
│   ├── stations.ts      充电站接口
│   ├── records.ts       充电记录接口
│   └── charts.ts        图表统计接口
├── assets/
│   ├── styles/
│   │   └── variables.css CSS 变量设计系统
│   └── main.css          全局样式
├── components/
│   ├── layout/           布局组件
│   │   ├── AppLayout.vue 整体布局
│   │   └── Sidebar.vue   侧边导航
│   ├── dashboard/        仪表盘组件
│   │   ├── SummaryCards.vue  概览卡片
│   │   └── ChartsPanel.vue   统计图表
│   ├── stations/         充电站组件
│   │   ├── StationQueryDialog.vue     查询弹窗
│   │   ├── StationResultsDialog.vue   结果表格
│   │   └── StationDetailDialog.vue    详情弹窗
│   └── records/          充电记录组件
│       ├── RecordQueryDialog.vue      查询弹窗
│       ├── RecordResultsDialog.vue    结果表格
│       └── RecordDetailDialog.vue     详情弹窗
├── router/
│   └── index.ts          路由配置
├── stores/
│   └── app.ts            Pinia 状态管理
├── views/
│   ├── DashboardView.vue      仪表盘页面
│   └── DataOverviewView.vue   数据总览页面
├── App.vue               根组件
└── main.ts               应用入口
```

## 3. 应用入口 main.ts

`main.ts` 是整个应用的起点：

```typescript
import './assets/main.css'
import 'element-plus/dist/index.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

// 全局注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
```

代码顺序解释：

```text
1. 导入全局样式
2. 导入 Element Plus 样式
3. 创建 Vue 应用实例
4. 注册所有 Element Plus 图标为全局组件
5. 安装 Pinia（状态管理）
6. 安装 Vue Router（路由）
7. 安装 Element Plus（UI 组件库）
8. 挂载到 #app DOM 节点
```

## 4. 根组件 App.vue

`App.vue` 是应用的根组件。重构后代码非常精简：

```vue
<script setup lang="ts">
import AppLayout from './components/layout/AppLayout.vue'
</script>

<template>
  <AppLayout>
    <router-view />
  </AppLayout>
</template>
```

```text
AppLayout  提供侧边栏 + 主内容区的布局框架
router-view 根据当前路由显示对应的页面组件
```

通过 `<slot />` 机制，`router-view` 渲染的内容会插入到 `AppLayout` 的主内容区。

## 5. 布局组件 AppLayout

`AppLayout.vue` 使用 Element Plus 的 Container 布局组件：

```vue
<template>
  <el-container class="app-shell">
    <el-aside :width="'var(--sidebar-width)'" class="app-sidebar">
      <Sidebar />
    </el-aside>
    <el-container class="app-main">
      <slot />    ← 这是 router-view 的内容
    </el-container>
  </el-container>
</template>
```

```text
el-container  外层容器（flex 布局）
el-aside      左侧固定侧边栏（260px 宽）
el-container  右侧主内容区
slot          这里插入页面内容
```

侧边栏固定在左侧，主内容区可滚动。

## 6. 侧边导航 Sidebar

`Sidebar.vue` 使用 Element Plus 的 Menu 组件：

```vue
<el-menu :default-active="route.path" background-color="transparent">
  <!-- 品牌标识 -->
  <div class="sidebar-brand">...</div>

  <!-- 导航菜单项 -->
  <el-menu-item index="/" @click="goDashboard">
    <el-icon><DataAnalysis /></el-icon><span>仪表盘</span>
  </el-menu-item>
  <el-menu-item index="/overview" @click="goOverview">
    <el-icon><Grid /></el-icon><span>数据总览</span>
  </el-menu-item>

  <!-- 快捷查询按钮（自定义，不在 el-menu 内） -->
  <div class="sidebar-action-btn" @click="openQuery('stations')">
    <el-icon><MapLocation /></el-icon><span>充电站查询</span>
  </div>
</el-menu>
```

```text
:default-active="route.path"  当前高亮项由路由路径决定
background-color="transparent" 使用 CSS 变量控制颜色
快捷查询按钮在 el-menu 外部，避免选中状态干扰
```

## 7. 页面视图 DashboardView

`DashboardView.vue` 是仪表盘页面，整合了多个子组件：

```vue
<script setup lang="ts">
import SummaryCards from '../components/dashboard/SummaryCards.vue'
import ChartsPanel from '../components/dashboard/ChartsPanel.vue'
import StationQueryDialog from '../components/stations/StationQueryDialog.vue'
// ... 其他组件

const stationResults = ref<StationListItem[]>([])
const recordResults = ref<RecordListItem[]>([])

function onStationResults(data: StationListItem[]) {
  stationResults.value = data
}
</script>

<template>
  <div class="page-container">
    <div class="topbar">
      <h1>仪表盘</h1>
      <el-button-group>
        <el-button @click="openQuery('stations')">充电站查询</el-button>
        <el-button @click="openQuery('records')">充电记录查询</el-button>
      </el-button-group>
    </div>

    <SummaryCards />         ← 概览卡片
    <ChartsPanel />           ← 统计图表

    <!-- 条件渲染两个查询弹窗 -->
    <StationQueryDialog v-if="activeModule === 'stations'" @results="onStationResults" />
    <RecordQueryDialog v-if="activeModule === 'records'" @results="onRecordResults" />
  </div>
</template>
```

```text
v-if="activeModule === 'stations'"  确保同一时间只渲染一个查询弹窗
@results 事件从子组件接收查询结果
```

## 8. 数据总览页面 DataOverviewView

`DataOverviewView.vue` 展示全维度数据分析：

```text
页面结构：
┌─ 顶部统计数值（4个卡片） ─────────────────┐
│  充电站 | 充电记录 | 城市/区县 | 运营商    │
├─ 6个 ECharts 图表（每行3个） ────────────┤
│  站点分布 | 运营商占比 | 支付方式分布      │
│  记录分布 | 平均费用 | 平均电量           │
├─ 数据表格 ───────────────────────────────┤
│  运营商信息 | 充电桩规格 | 站点样本 | 记录样本│
└────────────────────────────────────────────┘
```

图表数据全部来自后端的 SQL 聚合查询，不依赖前端样本数据。

## 9. 弹窗组件设计

查询系统采用三级弹窗结构，对应三个独立组件：

```text
第一级：查询弹窗（QueryDialog）
  ┌─────────────────────┐
  │  城市下拉框          │
  │  运营商下拉框         │
  │  关键词输入框         │
  │  [取消] [查询]       │
  └─────────┬───────────┘
            ▼ 点击查询
第二级：结果弹窗（ResultsDialog）
  ┌─────────────────────┐
  │  数据表格            │
  │  点击行 → 查看详情    │
  └─────────┬───────────┘
            ▼ 点击行
第三级：详情弹窗（DetailDialog）
  ┌─────────────────────┐
  │  详细信息列表         │
  │  16~18个字段         │
  └─────────────────────┘
```

每个弹窗都是一个独立的 `.vue` 文件，通过 Pinia 状态控制可见性。

## 10. 查询弹窗示例（StationQueryDialog）

充电站查询弹窗的实现：

```vue
<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { getCities, type City } from '../../api/cities'
import { getOperators, type Operator } from '../../api/operators'
import { getStations, type StationListItem } from '../../api/stations'
import { useAppStore } from '../../stores/app'

const appStore = useAppStore()
const cities = ref<City[]>([])
const operators = ref<Operator[]>([])

// 组件挂载时立即加载下拉数据
onMounted(async () => {
  const [cityData, operatorData] = await Promise.all([getCities(), getOperators()])
  cities.value = cityData
  operators.value = operatorData
})

// 查询参数
const query = reactive({
  city_id: undefined,
  operator_id: undefined,
  keyword: '',
})

async function runQuery() {
  loading.value = true
  const data = await getStations({
    city_id: query.city_id,
    operator_id: query.operator_id,
    keyword: query.keyword.trim() || undefined,
  })
  emit('results', data)          // 把结果传给父组件
  appStore.openResults()         // 切换到结果弹窗
  loading.value = false
}
</script>
```

```text
onMounted 中加载下拉数据，不依赖 @open 事件
未传的参数用 undefined，后端 FastAPI 会识别为 None
emit('results', data) 把查询结果传给父组件
appStore.openResults() 切换状态，显示结果弹窗
```

## 11. 结果弹窗示例（StationResultsDialog）

```vue
<template>
  <el-dialog v-model="resultsVisible" title="查询结果">
    <el-table :data="props.data" @row-click="viewDetail">
      <el-table-column prop="station_name" label="站点名称" />
      <el-table-column prop="city_name" label="城市" />
      <el-table-column prop="operator_name" label="运营商" />
    </el-table>
  </el-dialog>
</template>
```

```text
el-table 绑定 @row-click 事件
点击行触发 viewDetail，调用详情接口
```

## 12. 详情弹窗示例（StationDetailDialog）

```vue
<template>
  <el-dialog v-model="detailVisible" title="充电站详情">
    <el-descriptions :column="2" border>
      <el-descriptions-item label="站点名称">{{ data.station_name }}</el-descriptions-item>
      <el-descriptions-item label="城市">{{ data.city_name }}</el-descriptions-item>
      <el-descriptions-item label="地址">{{ data.address }}</el-descriptions-item>
      <el-descriptions-item label="功率">{{ data.power_kw }} kW</el-descriptions-item>
      <!-- 更多字段 -->
    </el-descriptions>
  </el-dialog>
</template>
```

```text
el-descriptions 适合展示键值对类型的数据
:column="2" 表示每行显示 2 个字段
border 带边框样式
```

## 13. API 请求模块

`/src/api/` 目录下每个文件对应一个后端资源：

```text
http.ts         Axios 实例，配置 baseURL
cities.ts       城市相关接口
operators.ts    运营商相关接口
chargerSpecs.ts 充电桩规格接口
stations.ts     充电站查询接口
records.ts      充电记录查询接口
charts.ts       图表统计接口
```

### 13.1 Axios 实例（http.ts）

```typescript
import axios from 'axios'

export const http = axios.create({
  baseURL: 'http://127.0.0.1:8000',   // 后端地址
  timeout: 10000,                       // 10秒超时
})
```

```text
baseURL 指向 FastAPI 后端
所有 API 请求都通过这个实例发送
```

### 13.2 API 调用示例（stations.ts）

```typescript
import { http } from './http'

// 定义接口返回的数据类型
export interface StationListItem {
  station_id: number
  station_name: string
  city_name: string
  operator_name: string
  type_name: string
  power_kw: number | null
}

// 定义查询参数类型
export interface StationQuery {
  city_id?: number
  operator_id?: number
  keyword?: string
}

// GET 请求，查询参数通过 params 传递
export async function getStations(query: StationQuery = {}) {
  const response = await http.get<{ data: StationListItem[] }>('/api/stations', {
    params: query,
  })
  return response.data.data   // 解包，只返回 data 数组
}
```

```text
http.get<T>  泛型参数 T 指定响应数据类型
params        自动拼接成 URL 查询参数
return response.data.data  只返回有用数据，不暴露 HTTP 封装
```

### 13.3 图表 API 示例（charts.ts）

```typescript
export interface ChartPoint {
  name: string
  value: number
}

export async function getStationsByCityChart() {
  const response = await http.get<{ data: ChartPoint[] }>('/api/charts/stations-by-city')
  return response.data.data
}
```

所有图表接口返回相同的数据结构 `{ name, value }`，前端统一处理。

## 14. ECharts 图表渲染

以仪表盘的柱状图为例：

```typescript
import * as echarts from 'echarts'

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

onMounted(() => {
  // 初始化图表
  chartInstance = echarts.init(chartRef.value!)
  chartInstance.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['章贡区', '定南县', ...] },
    yAxis: { type: 'value' },
    series: [{
      type: 'bar',
      data: [120, 85, ...],
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#10b981' },
          { offset: 1, color: '#d1fae5' },
        ]),
      },
    }],
  })

  // 窗口变化时自适应
  window.addEventListener('resize', () => chartInstance?.resize())
})

onBeforeUnmount(() => {
  chartInstance?.dispose()  // 组件销毁时释放资源
})
```

```text
echarts.init(dom)  初始化图表实例
setOption()        设置图表配置项
resize()           窗口变化时自适应
dispose()          组件销毁时释放资源
图表容器 <div ref="chartRef" style="width:100%;height:230px">
```

## 15. 放大图表功能

每个图表卡片右上角都有一个放大按钮：

```vue
<el-card>
  <template #header>
    <div class="chart-card-header">
      <strong>各区县站点数量</strong>
      <el-button size="small" circle :icon="FullScreen" @click="openZoom('city')" />
    </div>
  </template>
  <div ref="cityChartRef" class="chart-box"></div>
</el-card>
```

```text
点击放大按钮 → 打开 el-dialog
dialog 的 @opened 事件触发后初始化 ECharts
图表在大尺寸容器中重新渲染（字体放大、间距变大）
```

## 16. CSS 变量设计系统

在 `variables.css` 中定义全局样式变量：

```css
:root {
  --primary: #10b981;           /* 主色-翠绿 */
  --sidebar-bg: #0f172a;        /* 侧边栏背景-深蓝 */
  --bg-page: #f1f5f9;           /* 页面背景-浅灰 */
  --bg-card: #ffffff;            /* 卡片背景-白色 */
  --text-primary: #1e293b;      /* 主文字色 */
  --text-secondary: #64748b;    /* 次要文字色 */
  --radius-md: 10px;            /* 圆角 */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
}
```

```text
CSS 变量让全局配色统一
修改一个变量即可改变整体主题
所有组件文件通过 var(--primary) 引用
```

## 17. 常见问题

### 17.1 页面空白

可能原因：

```text
1. 后端未启动，API 调用失败
2. 路由配置错误，找不到页面
3. 组件导入路径错误
```

### 17.2 图表不显示

```text
1. ECharts 容器没有设置宽高
2. 数据为空数组
3. DOM 未挂载时调用了 init
4. el-dialog 中的图表需在 @opened 事件中初始化
```

### 17.3 弹窗不出现

```text
1. Pinia 状态中的 visible 没有被设置为 true
2. 组件被 v-if 条件排除
3. 两个弹窗绑定同一个 v-model
```

### 17.4 构建命令

```powershell
npm run dev            # 开发模式
npm run build          # 生产构建
npm run type-check     # TypeScript 类型检查
```

## 18. 实验报告可用描述

可以在实验报告中写：

```text
前端采用 Vue 3 + TypeScript 开发，使用 Element Plus 组件库构建界面。项目采用组件化架构，将页面拆分为布局组件（AppLayout、Sidebar）、业务组件（查询弹窗、结果表格、详情弹窗）和视图页面（仪表盘、数据总览）。状态管理使用 Pinia 控制弹窗的打开关闭，路由使用 Vue Router 实现页面切换。数据可视化使用 ECharts 实现柱状图、环形饼图、横向柱状图等多种图表类型，图表数据全部来自后端聚合查询接口。

前端全局样式采用 CSS 变量设计系统，在 variables.css 中定义主色、背景色、文字色、圆角、阴影等统一变量。仪表盘概览卡片展示充电站 2402 条、充电记录 1000 条等核心统计数据。每个图表卡片右上角配有放大按钮，点击后可在对话框中查看大图。
```
