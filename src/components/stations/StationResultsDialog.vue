<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useAppStore } from '../../stores/app'
import { getStationDetail, type StationDetail, type StationListItem } from '../../api/stations'
import { ElMessage } from 'element-plus'
import { ref } from 'vue'

const appStore = useAppStore()
const { resultsVisible } = storeToRefs(appStore)

const props = defineProps<{ data: StationListItem[] }>()
const emit = defineEmits<{
  viewDetail: [data: StationDetail]
}>()

const loading = ref(false)

function displayValue(value: string | number | boolean | null | undefined, suffix = '') {
  if (value === null || value === undefined || value === '') return '-'
  return `${value}${suffix}`
}

async function viewDetail(row: StationListItem) {
  loading.value = true
  try {
    const detail = await getStationDetail(row.station_id)
    emit('viewDetail', detail)
    appStore.openDetail()
  } catch {
    ElMessage.error('详情加载失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <el-dialog
    v-model="resultsVisible"
    title="充电站查询结果"
    width="960px"
    :close-on-click-modal="false"
  >
    <el-table
      :data="props.data"
      v-loading="loading"
      border
      stripe
      highlight-current-row
      @row-click="viewDetail"
      style="cursor: pointer"
    >
      <el-table-column type="index" label="序号" width="60" align="center" />
      <el-table-column prop="station_name" label="站点名称" min-width="220" show-overflow-tooltip />
      <el-table-column prop="city_name" label="城市" width="100" />
      <el-table-column prop="operator_name" label="运营商" width="130" />
      <el-table-column prop="type_name" label="充电桩类型" width="130" />
      <el-table-column label="功率" width="100" align="center">
        <template #default="{ row }">{{ displayValue(row.power_kw, ' kW') }}</template>
      </el-table-column>
    </el-table>
    <template #footer>
      <span class="dialog-footer-info">共 {{ props.data.length }} 条记录，点击行查看详情</span>
      <el-button @click="resultsVisible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.dialog-footer-info {
  color: var(--text-tertiary);
  font-size: 13px;
}
</style>
