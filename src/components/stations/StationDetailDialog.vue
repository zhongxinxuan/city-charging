<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useAppStore } from '../../stores/app'
import type { StationDetail } from '../../api/stations'

const appStore = useAppStore()
const { detailVisible } = storeToRefs(appStore)

const props = defineProps<{ data: StationDetail | null }>()

function displayValue(value: string | number | boolean | null | undefined, suffix = '') {
  if (value === null || value === undefined || value === '') return '-'
  if (typeof value === 'boolean') return value ? '是' : '否'
  return `${value}${suffix}`
}

function close() {
  appStore.closeAll()
}
</script>

<template>
  <el-dialog
    v-model="detailVisible"
    title="充电站详情"
    width="720px"
    :close-on-click-modal="false"
  >
    <template v-if="data">
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="站点名称" :span="2">{{ data.station_name }}</el-descriptions-item>
        <el-descriptions-item label="城市">{{ data.city_name }}</el-descriptions-item>
        <el-descriptions-item label="运营商">{{ data.operator_name }}</el-descriptions-item>
        <el-descriptions-item label="充电桩类型">{{ data.type_name }}</el-descriptions-item>
        <el-descriptions-item label="功率">{{ displayValue(data.power_kw, ' kW') }}</el-descriptions-item>
        <el-descriptions-item label="电压">{{ displayValue(data.voltage_v, ' V') }}</el-descriptions-item>
        <el-descriptions-item label="电流">{{ displayValue(data.current_a, ' A') }}</el-descriptions-item>
        <el-descriptions-item label="接口类型">{{ displayValue(data.connector_type) }}</el-descriptions-item>
        <el-descriptions-item label="充电时长">{{ displayValue(data.charge_time_min, ' 分钟') }}</el-descriptions-item>
        <el-descriptions-item label="每度电价格">{{ displayValue(data.cost_per_kwh, ' 元/kWh') }}</el-descriptions-item>
        <el-descriptions-item label="开放时间" :span="2">{{ displayValue(data.opening_hours) }}</el-descriptions-item>
        <el-descriptions-item label="地址" :span="2">{{ displayValue(data.address) }}</el-descriptions-item>
        <el-descriptions-item label="电话">{{ displayValue(data.phone) }}</el-descriptions-item>
        <el-descriptions-item label="停车位">{{ displayValue(data.parking_spots, ' 个') }}</el-descriptions-item>
        <el-descriptions-item label="卫生间">{{ data.has_restroom ? '有' : '无' }}</el-descriptions-item>
        <el-descriptions-item label="经纬度">{{ displayValue(data.longitude) }}, {{ displayValue(data.latitude) }}</el-descriptions-item>
      </el-descriptions>
    </template>
    <template #footer>
      <el-button @click="close">关闭</el-button>
    </template>
  </el-dialog>
</template>
