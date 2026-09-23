<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useAppStore } from '../../stores/app'
import type { RecordDetail } from '../../api/records'

const appStore = useAppStore()
const { detailVisible } = storeToRefs(appStore)

const props = defineProps<{ data: RecordDetail | null }>()

function formatDateTime(value: string | null) {
  if (!value) return '-'
  return value.replace('T', ' ')
}

function displayValue(value: string | number | null | undefined, suffix = '') {
  if (value === null || value === undefined || value === '') return '-'
  return `${value}${suffix}`
}

function close() {
  appStore.closeAll()
}
</script>

<template>
  <el-dialog
    v-model="detailVisible"
    title="充电记录详情"
    width="720px"
    :close-on-click-modal="false"
  >
    <template v-if="data">
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="记录编号" :span="2">{{ data.record_id }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ data.username }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ displayValue(data.phone) }}</el-descriptions-item>
        <el-descriptions-item label="用户类型">{{ displayValue(data.user_type) }}</el-descriptions-item>
        <el-descriptions-item label="车辆类型">{{ displayValue(data.vehicle_type) }}</el-descriptions-item>
        <el-descriptions-item label="车辆型号" :span="2">{{ displayValue(data.vehicle_model) }}</el-descriptions-item>
        <el-descriptions-item label="站点名称" :span="2">{{ data.station_name }}</el-descriptions-item>
        <el-descriptions-item label="城市">{{ data.city_name }}</el-descriptions-item>
        <el-descriptions-item label="开始 SOC">{{ displayValue(data.start_soc, '%') }}</el-descriptions-item>
        <el-descriptions-item label="结束 SOC">{{ displayValue(data.end_soc, '%') }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ formatDateTime(data.charge_start_time) }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ formatDateTime(data.charge_end_time) }}</el-descriptions-item>
        <el-descriptions-item label="充电时长">{{ displayValue(data.duration_minutes, ' 分钟') }}</el-descriptions-item>
        <el-descriptions-item label="充电电量">{{ displayValue(data.energy_kwh, ' kWh') }}</el-descriptions-item>
        <el-descriptions-item label="费用">{{ displayValue(data.cost_yuan, ' 元') }}</el-descriptions-item>
        <el-descriptions-item label="支付方式">{{ displayValue(data.payment_method) }}</el-descriptions-item>
      </el-descriptions>
    </template>
    <template #footer>
      <el-button @click="close">关闭</el-button>
    </template>
  </el-dialog>
</template>
