<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { storeToRefs } from 'pinia'
import { getCities, type City } from '../../api/cities'
import { getRecords, type RecordListItem, type RecordQuery } from '../../api/records'
import { useAppStore } from '../../stores/app'

const emit = defineEmits<{
  results: [data: RecordListItem[]]
}>()

const appStore = useAppStore()
const { queryVisible } = storeToRefs(appStore)

const cities = ref<City[]>([])
const loading = ref(false)

const query = reactive<RecordQuery>({
  city_id: undefined,
  payment_method: '',
  keyword: '',
})

const paymentMethods = ['微信支付', '支付宝', '信用卡', '现金']

onMounted(async () => {
  try {
    cities.value = await getCities()
  } catch {
    ElMessage.error('基础数据加载失败')
  }
})

async function runQuery() {
  loading.value = true
  try {
    const params: RecordQuery = {
      city_id: query.city_id,
      payment_method: query.payment_method || undefined,
      keyword: query.keyword?.trim() || undefined,
    }
    const data = await getRecords(params)
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
    title="充电记录查询"
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
          <el-form-item label="支付方式">
            <el-select v-model="query.payment_method" clearable placeholder="全部方式">
              <el-option v-for="m in paymentMethods" :key="m" :label="m" :value="m" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-form-item label="关键词">
            <el-input v-model="query.keyword" clearable placeholder="记录编号、用户或站点" />
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
