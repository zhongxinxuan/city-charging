<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useAppStore } from '../../stores/app'
import { getRecordDetail, type RecordDetail, type RecordListItem } from '../../api/records'
import { ElMessage } from 'element-plus'
import { ref } from 'vue'

const appStore = useAppStore()
const { resultsVisible } = storeToRefs(appStore)

const props = defineProps<{ data: RecordListItem[] }>()
const emit = defineEmits<{
  viewDetail: [data: RecordDetail]
}>()

const loading = ref(false)

function formatDateTime(value: string | null) {
  if (!value) return '-'
  return value.replace('T', ' ')
}

function displayValue(value: string | number | null | undefined, suffix = '') {
  if (value === null || value === undefined || value === '') return '-'
  return `${value}${suffix}`
}

async function viewDetail(row: RecordListItem) {
  loading.value = true
  try {
    const detail = await getRecordDetail(row.record_id)
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
    title="充电记录查询结果"
    width="1100px"
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
      <el-table-column prop="record_id" label="记录编号" width="140" />
      <el-table-column prop="username" label="用户" width="100" />
      <el-table-column prop="station_name" label="站点名称" min-width="180" show-overflow-tooltip />
      <el-table-column prop="city_name" label="城市" width="90" />
      <el-table-column label="开始时间" width="170">
        <template #default="{ row }">{{ formatDateTime(row.charge_start_time) }}</template>
      </el-table-column>
      <el-table-column label="电量" width="100" align="center">
        <template #default="{ row }">{{ displayValue(row.energy_kwh, ' kWh') }}</template>
      </el-table-column>
      <el-table-column label="费用" width="100" align="center">
        <template #default="{ row }">{{ displayValue(row.cost_yuan, ' 元') }}</template>
      </el-table-column>
      <el-table-column prop="payment_method" label="支付方式" width="100" align="center" />
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
