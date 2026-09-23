# 前端路由与状态管理教程

本文档说明"城市充电桩信息查询系统"前端项目中的路由配置（Vue Router）和状态管理（Pinia）设计与实现。

## 1. 路由和状态管理的作用

```text
Vue Router（路由）：
  控制页面切换 — 仪表盘页面 / 数据总览页面

Pinia（状态管理）：
  控制组件状态 — 弹窗开关 / 当前模块 / 统计数据
```

两者分工：

```text
路由 → 导航到哪个页面
状态 → 页面上组件怎么显示
```

## 2. Vue Router 配置

路由配置文件：

```text
src/router/index.ts
```

### 2.1 路由定义

```typescript
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),   // HTML5 历史模式
  routes: [
    {
      path: '/',                  // 根路径
      name: 'dashboard',          // 路由名称
      component: () => import('../views/DashboardView.vue'),  // 懒加载
    },
    {
      path: '/overview',          // /overview 路径
      name: 'overview',
      component: () => import('../views/DataOverviewView.vue'),
    },
  ],
})

export default router
```

```text
createWebHistory()  使用 HTML5 的 history API，URL 不带 #
懒加载 ()=>import()  只有访问该路由时才加载对应组件
```

### 2.2 路由使用

在 `main.ts` 中注册：

```typescript
import router from './router'
app.use(router)
```

在 `App.vue` 中使用：

```vue
<template>
  <AppLayout>
    <router-view />    ← 路由匹配的页面在此渲染
  </AppLayout>
</template>
```

```text
<router-view />  根据当前 URL 渲染对应的页面组件
```

### 2.3 页面导航

在侧边栏中通过 `router.push()` 切换页面：

```typescript
import { useRouter } from 'vue-router'
const router = useRouter()

function goDashboard() {
  router.push('/')
}

function goOverview() {
  router.push('/overview')
}
```

```text
router.push('/')        跳转到仪表盘
router.push('/overview') 跳转到数据总览
```

### 2.4 路由高亮

侧边栏的菜单高亮通过当前路由路径控制：

```typescript
import { useRoute } from 'vue-router'
const route = useRoute()

// :default-active="route.path"
// route.path === '/'       → 仪表盘高亮
// route.path === '/overview' → 数据总览高亮
```

```text
route.path 始终是当前 URL 路径
el-menu 的 default-active 绑定 route.path
页面切换时自动更新高亮
```

## 3. Pinia 状态管理

状态管理文件：

```text
src/stores/app.ts
```

### 3.1 Store 定义

```typescript
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 状态定义
  // 计算属性
  // 方法定义
  return { ... }
})
```

```text
defineStore('app', () => {...})  定义名为 app 的 Store
setup 语法（Composition API）    和 Vue 组件写法一致
```

### 3.2 状态变量

```typescript
// 当前选中的模块
const activeModule = ref<ModuleKey>('stations')
// 模块类型：'stations' | 'records'

// 三级弹窗的可见性
const queryVisible = ref(false)    // 查询弹窗
const resultsVisible = ref(false)  // 结果弹窗
const detailVisible = ref(false)   // 详情弹窗

// 静态统计数据
const stationCount = ref(2402)
const recordCount = ref(1000)
const userCount = ref(500)
```

```text
activeModule  控制当前显示哪种查询（充电站 or 充电记录）
queryVisible  查询弹窗是否打开
resultsVisible 结果弹窗是否打开
detailVisible  详情弹窗是否打开
```

### 3.3 计算属性

```typescript
// 当前是否为充电站模块
const isStationsModule = computed(() => activeModule.value === 'stations')
```

```text
isStationsModule 为 true  → 显示充电站相关内容
isStationsModule 为 false → 显示充电记录相关内容
```

### 3.4 方法定义

```typescript
// 打开查询弹窗
function openQuery(moduleKey: ModuleKey) {
  activeModule.value = moduleKey   // 设置当前模块
  queryVisible.value = true        // 打开查询弹窗
  resultsVisible.value = false     // 关闭结果弹窗
  detailVisible.value = false      // 关闭详情弹窗
}

// 打开结果弹窗
function openResults() {
  queryVisible.value = false
  resultsVisible.value = true
}

// 打开详情弹窗
function openDetail() {
  detailVisible.value = true
}

// 关闭所有弹窗
function closeAll() {
  queryVisible.value = false
  resultsVisible.value = false
  detailVisible.value = false
}
```

状态切换流程：

```text
点击"充电站查询"
  ↓ openQuery('stations')
activeModule = 'stations'
queryVisible = true
  ↓ 点击"查询"
  ↓ openResults()
queryVisible = false
resultsVisible = true
  ↓ 点击表格行
  ↓ openDetail()
detailVisible = true
  ↓ 点击"关闭"
  ↓ closeAll()
所有 visible = false
```

## 4. 弹窗控制机制

弹窗通过 `v-model` 绑定 Pinia 中的 visible 变量：

```vue
<!-- 查询弹窗 -->
<el-dialog v-model="queryVisible" title="充电站查询">
```

```text
v-model="queryVisible"  绑定 Pinia 的 queryVisible 状态
当 Store 中 queryVisible = true 时弹窗打开
当用户点击弹窗的 X 按钮时 queryVisible = false
```

查询弹窗和结果弹窗使用 `v-if` 条件渲染：

```vue
<StationQueryDialog v-if="activeModule === 'stations'" />
<RecordQueryDialog v-if="activeModule === 'records'" />
```

```text
同一时间只会渲染一个查询弹窗
activeModule = 'stations'  → 充电站查询弹窗
activeModule = 'records'   → 充电记录查询弹窗
```

## 5. 在组件中使用 Store

```typescript
import { useAppStore } from '../../stores/app'
import { storeToRefs } from 'pinia'

const appStore = useAppStore()

// 方式1：直接访问（会丢失响应性，不推荐在模板中使用）
appStore.queryVisible = true

// 方式2：解构为 ref（保持响应性，推荐）
const { queryVisible, resultsVisible, detailVisible } = storeToRefs(appStore)
// queryVisible.value 是响应式的

// 方式3：直接调用 store 的方法
appStore.openQuery('stations')
appStore.openResults()
```

```text
storeToRefs()  将 Store 属性转为 ref，保持响应性
直接解构 const { queryVisible } = appStore 会丢失响应性
方法（函数）不需要 storeToRefs，可以直接调用
```

## 6. 完整页面交互流程

### 6.1 在仪表盘页面

```text
用户打开页面
  ↓
默认显示仪表盘（/ 路由）
  ↓
点击"充电站查询"按钮
  ↓
openQuery('stations')
  ↓
activeModule = 'stations'
queryVisible = true
  ↓
StationQueryDialog 渲染（v-if 条件满足）
  ↓
弹窗显示，城市和运营商下拉框已自动加载数据
```

### 6.2 查询到详情

```text
填写查询条件，点击"查询"
  ↓
StationQueryDialog 调用 getStations()
  ↓
emit('results', data) 把结果传给 DashboardView
  ↓
appStore.openResults()
  ↓
resultsVisible = true，显示 StationResultsDialog
  ↓
在结果表格中点击某一行
  ↓
StationResultsDialog 调用 getStationDetail()
  ↓
emit('viewDetail', detail) 传给父组件
  ↓
appStore.openDetail()
  ↓
StationDetailDialog 显示，展示 16 个字段的详情
```

### 6.3 路由切换

```text
在仪表盘页面（/）
  ↓
点击侧边栏"数据总览"
  ↓
router.push('/overview')
  ↓
router-view 切换为 DataOverviewView 组件
  ↓
URL 变为 /overview
  ↓
所有查询弹窗关闭（因为 DashboardView 被销毁）
```

## 7. 从侧边栏打开查询

侧边栏的快捷查询按钮可以在任意页面打开查询弹窗：

```typescript
function openQuery(moduleKey: ModuleKey) {
  // 如果不在仪表盘页面，先跳转过去
  if (route.path !== '/') {
    router.push('/')          // 先导航到仪表盘
    setTimeout(() => appStore.openQuery(moduleKey), 100)  // 等组件就绪
  } else {
    appStore.openQuery(moduleKey)  // 已经在仪表盘，直接打开
  }
}
```

```text
查询弹窗（StationQueryDialog / RecordQueryDialog）只在 DashboardView 中渲染
如果用户在数据总览页面，需要先跳转到仪表盘
setTimeout(100ms) 确保 DashboardView 挂载完毕
```

## 8. 状态管理对比

如果不使用 Pinia，可能的方式：

```text
方式1：每个弹窗自己维护 visible
  问题：父子组件通信复杂，需要用 emit 层层传递

方式2：Provide / Inject
  问题：跨多级组件传递时类型不清晰，调试困难

方式3：全局事件总线
  问题：事件名难管理，容易冲突
```

使用 Pinia 的优势：

```text
1. 集中管理：所有状态在一个 Store 中
2. 响应式：修改状态自动触发视图更新
3. 类型安全：TypeScript 类型推导
4. 跨组件：任意组件都可以访问和修改
5. DevTools：支持 Vue Devtools 调试
```

## 9. 常见问题

### 9.1 弹窗不出现

```text
1. 检查 Store 中的 visible 是否被设置为 true
2. 检查组件上的 v-if 条件是否满足
3. 检查 v-model 绑定的变量是否正确
```

### 9.2 路由不匹配

```text
1. 检查 router/index.ts 中的路径定义
2. 检查 router.push() 的参数
3. 检查 router-view 是否在模板中
```

### 9.3 storeToRefs 和直接解构的区别

```typescript
// 错误：失去响应性
const { queryVisible } = appStore
// queryVisible 是一个普通值，修改不会触发更新

// 正确：保持响应性
const { queryVisible } = storeToRefs(appStore)
// queryVisible 是 ref，修改会触发更新
```

## 10. 实验报告可用描述

可以在实验报告中写：

```text
前端使用 Vue Router 实现页面路由，配置了仪表盘（/）和数据总览（/overview）两个路由，采用懒加载方式按需加载页面组件。侧边栏通过 router.push 实现页面切换，el-menu 的 default-active 绑定 route.path 实现菜单高亮。

状态管理使用 Pinia 定义了一个全局 Store，管理弹窗可见性（查询弹窗、结果弹窗、详情弹窗）和当前模块切换。三级弹窗通过 openQuery、openResults、openDetail 和 closeAll 方法控制，弹窗组件使用 v-if 条件渲染避免同时出现。Store 中的变量通过 storeToRefs 解构到组件中以保持响应性。
```
