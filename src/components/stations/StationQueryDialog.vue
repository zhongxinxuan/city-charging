<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { storeToRefs } from 'pinia'
import { getCities, type City } from '../../api/cities'
import { getOperators, type Operator } from '../../api/operators'
import { getStations, type StationListItem, type StationQuery } from '../../api/stations'
import { useAppStore } from '../../stores/app'

const emit = defineEmits<{
  results: [data: StationListItem[]]
}>()

const appStore = useAppStore()
const { queryVisible } = storeToRefs(appStore)

const cities = ref<City[]>([])
const operators = ref<Operator[]>([])
const loading = ref(false)

const query = reactive<StationQuery>({
  city_id: undefined,
  operator_id: undefined,
  keyword: '',
})

onMounted(async () => {
  try {
    const [cityData, operatorData] = await Promise.all([getCities(), getOperators()])
    cities.value = cityData
    operators.value = operatorData
  } catch {
    ElMessage.error('基础数据加载失败')
  }
})

async function runQuery() {
  loading.value = true
  try {
    const params: StationQuery = {
      city_id: query.city_id,
      operator_id: query.operator_id,
      keyword: query.keyword?.trim() || undefined,
    }
    const data = await getStations(params)
    emit('results', data)
    appStore.openResults()
  } catch {
    ElMessage.error('查询失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <el-dialog
    v-model="queryVisible"
    title="充电站查询"
    width="680px"
    :close-on-click-modal="false"
  >
    <el-form label-position="top" class="query-form">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="8">
          <el-form-item label="城市">
            <el-select v-model="query.city_id" clearable placeholder="全部城市">
              <el-option
                v-for="city in cities"
                :key="city.city_id"
                :label="city.city_name"
                :value="city.city_id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-form-item label="运营商">
            <el-select v-model="query.operator_id" clearable placeholder="全部运营商">
              <el-option
                v-for="op in operators"
                :key="op.operator_id"
                :label="op.operator_name"
                :value="op.operator_id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-form-item label="关键词">
            <el-input v-model="query.keyword" clearable placeholder="站点名称或地址" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <template #footer>
      <el-button @click="queryVisible = false">取消</el-button>
      <el-button type="primary" :icon="Search" :loading="loading" @click="runQuery">查询</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.query-form {
  padding: 8px 0;
}
</style>
