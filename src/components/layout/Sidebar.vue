<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAppStore, type ModuleKey } from '../../stores/app'
import {
  Monitor,
  Document,
  DataAnalysis,
  Grid,
  MapLocation,
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

function goDashboard() {
  router.push('/')
}

function goOverview() {
  router.push('/overview')
}

function openQuery(moduleKey: ModuleKey) {
  if (route.path !== '/') {
    router.push('/')
    setTimeout(() => appStore.openQuery(moduleKey), 100)
  } else {
    appStore.openQuery(moduleKey)
  }
}
</script>

<template>
  <div class="sidebar-container">
    <el-menu
      :default-active="route.path"
      background-color="transparent"
      text-color="var(--sidebar-text)"
      active-text-color="var(--sidebar-text-active)"
      class="sidebar-menu"
    >
      <div class="sidebar-brand">
        <div class="sidebar-logo">
          <el-icon :size="22"><Monitor /></el-icon>
        </div>
        <div class="sidebar-title">
          <strong>充电桩查询系统</strong>
          <span>赣州市公共充电数据</span>
        </div>
      </div>

      <div class="sidebar-divider" />

      <el-menu-item index="/" @click="goDashboard">
        <el-icon><DataAnalysis /></el-icon>
        <span>仪表盘</span>
      </el-menu-item>

      <el-menu-item index="/overview" @click="goOverview">
        <el-icon><Grid /></el-icon>
        <span>数据总览</span>
      </el-menu-item>
    </el-menu>

    <div class="sidebar-actions">
      <div class="sidebar-divider" />
      <div class="sidebar-label">快捷查询</div>
      <div class="sidebar-action-btn" @click="openQuery('stations')">
        <el-icon :size="16"><MapLocation /></el-icon>
        <span>充电站查询</span>
      </div>
      <div class="sidebar-action-btn" @click="openQuery('records')">
        <el-icon :size="16"><Document /></el-icon>
        <span>充电记录查询</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sidebar-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-menu {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-right: none !important;
  padding: 0 12px;
  overflow-y: auto;
  min-height: 0;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 12px 20px;
  border-bottom: 1px solid var(--sidebar-border);
}

.sidebar-logo {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  background: var(--primary);
  color: white;
  flex-shrink: 0;
}

.sidebar-title strong {
  display: block;
  font-size: 15px;
  font-weight: 700;
  color: #f1f5f9;
  line-height: 1.3;
}

.sidebar-title span {
  display: block;
  font-size: 11px;
  color: var(--sidebar-text);
  margin-top: 2px;
}

.sidebar-divider {
  height: 1px;
  background: var(--sidebar-border);
  margin: 8px 12px;
}

.sidebar-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--sidebar-text);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 8px 12px 4px;
}

.el-menu-item {
  border-radius: var(--radius-sm) !important;
  margin: 2px 0;
  height: 42px !important;
  line-height: 42px !important;
}

.el-menu-item:hover {
  background: var(--sidebar-hover) !important;
}

.el-menu-item.is-active {
  background: var(--sidebar-active) !important;
  color: var(--sidebar-text-active) !important;
}

.sidebar-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 4px 12px;
}

.sidebar-action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  height: 42px;
  border-radius: var(--radius-sm);
  color: var(--sidebar-text);
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.sidebar-action-btn:hover {
  background: var(--sidebar-hover);
  color: var(--sidebar-text-active);
}
</style>
