<script setup lang="ts">
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { storeToRefs } from 'pinia'
import { useAppStore } from '../stores/app'
import type { ModuleKey } from '../stores/app'
import type { StationDetail, StationListItem } from '../api/stations'
import type { RecordDetail, RecordListItem } from '../api/records'

import SummaryCards from '../components/dashboard/SummaryCards.vue'
import ChartsPanel from '../components/dashboard/ChartsPanel.vue'
import StationQueryDialog from '../components/stations/StationQueryDialog.vue'
import StationResultsDialog from '../components/stations/StationResultsDialog.vue'
import StationDetailDialog from '../components/stations/StationDetailDialog.vue'
import RecordQueryDialog from '../components/records/RecordQueryDialog.vue'
import RecordResultsDialog from '../components/records/RecordResultsDialog.vue'
import RecordDetailDialog from '../components/records/RecordDetailDialog.vue'

const appStore = useAppStore()
const { activeModule } = storeToRefs(appStore)

const stationResults = ref<StationListItem[]>([])
const recordResults = ref<RecordListItem[]>([])
const selectedStation = ref<StationDetail | null>(null)
const selectedRecord = ref<RecordDetail | null>(null)

function onStationResults(data: StationListItem[]) {
  stationResults.value = data
}

function onRecordResults(data: RecordListItem[]) {
  recordResults.value = data
}

function onStationDetail(data: StationDetail) {
  selectedStation.value = data
  selectedRecord.value = null
}

function onRecordDetail(data: RecordDetail) {
  selectedRecord.value = data
  selectedStation.value = null
}

function openQuery(moduleKey: ModuleKey) {
  appStore.openQuery(moduleKey)
  selectedStation.value = null
  selectedRecord.value = null
}
</script>

<template>
  <div class="page-container">
    <div class="topbar">
      <div>
        <p class="eyebrow">赣州市公共充电服务数据</p>
        <h1>仪表盘</h1>
      </div>
      <el-button-group class="topbar-actions">
        <el-button type="primary" :icon="Search" @click="openQuery('stations')">
          充电站查询
        </el-button>
        <el-button :icon="Search" @click="openQuery('records')">
          充电记录查询
        </el-button>
      </el-button-group>
    </div>

    <SummaryCards />

    <ChartsPanel />

    <StationQueryDialog v-if="activeModule === 'stations'" @results="onStationResults" />
    <RecordQueryDialog v-if="activeModule === 'records'" @results="onRecordResults" />

    <StationResultsDialog
      v-if="activeModule === 'stations'"
      :data="stationResults"
      @view-detail="onStationDetail"
    />
    <RecordResultsDialog
      v-else
      :data="recordResults"
      @view-detail="onRecordDetail"
    />

    <StationDetailDialog
      v-if="selectedStation"
      :data="selectedStation"
    />
    <RecordDetailDialog
      v-if="selectedRecord"
      :data="selectedRecord"
    />
  </div>
</template>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 22px;
}

.eyebrow {
  margin: 0 0 4px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.topbar h1 {
  margin: 0;
  font-size: 26px;
  font-weight: 800;
  color: var(--text-primary);
}

.topbar-actions {
  flex-shrink: 0;
}
</style>
