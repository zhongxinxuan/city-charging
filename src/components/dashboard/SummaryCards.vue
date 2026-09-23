<script setup lang="ts">
import { useAppStore } from '../../stores/app'
import { ElIcon } from 'element-plus'
import {
  OfficeBuilding,
  Document,
  User,
  TrendCharts,
} from '@element-plus/icons-vue'

const appStore = useAppStore()

const overviewCards = [
  {
    label: '充电站总数',
    value: appStore.stationCount,
    icon: OfficeBuilding,
    color: 'var(--primary)',
    bg: 'var(--primary-light)',
    desc: '赣州市各区县充电基础设施',
  },
  {
    label: '充电记录总数',
    value: appStore.recordCount,
    icon: Document,
    color: 'var(--secondary)',
    bg: 'var(--secondary-light)',
    desc: '系统累计充电服务数据',
  },
  {
    label: '注册用户数',
    value: appStore.userCount,
    icon: User,
    color: 'var(--accent)',
    bg: 'var(--accent-light)',
    desc: '充电服务注册用户总量',
  },
  {
    label: '运营商数量',
    value: 5,
    icon: TrendCharts,
    color: '#8b5cf6',
    bg: '#f3e8ff',
    desc: '覆盖赣州市的充电运营商',
  },
]
</script>

<template>
  <div class="overview-grid">
    <el-card
      v-for="(card, index) in overviewCards"
      :key="index"
      shadow="never"
      class="stat-card"
    >
      <div class="stat-card-inner">
        <div class="stat-card-left">
          <span class="stat-label">{{ card.label }}</span>
          <span class="stat-number">{{ card.value.toLocaleString() }}</span>
          <span class="stat-desc">{{ card.desc }}</span>
        </div>
        <div class="stat-card-icon" :style="{ background: card.bg, color: card.color }">
          <el-icon :size="26"><component :is="card.icon" /></el-icon>
        </div>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

@media (max-width: 1200px) {
  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--border-color) !important;
}

.stat-card-inner {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.stat-card-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-number {
  font-size: 26px;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-desc {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

.stat-card-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
</style>
