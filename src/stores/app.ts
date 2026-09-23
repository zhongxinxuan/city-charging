import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export type ModuleKey = 'stations' | 'records'

export const useAppStore = defineStore('app', () => {
  const activeModule = ref<ModuleKey>('stations')
  const queryVisible = ref(false)
  const resultsVisible = ref(false)
  const detailVisible = ref(false)

  const isStationsModule = computed(() => activeModule.value === 'stations')

  const stationCount = ref(2402)
  const recordCount = ref(1000)
  const userCount = ref(500)

  function openQuery(moduleKey: ModuleKey) {
    activeModule.value = moduleKey
    queryVisible.value = true
    resultsVisible.value = false
    detailVisible.value = false
  }

  function openResults() {
    queryVisible.value = false
    resultsVisible.value = true
  }

  function openDetail() {
    detailVisible.value = true
  }

  function closeAll() {
    queryVisible.value = false
    resultsVisible.value = false
    detailVisible.value = false
  }

  return {
    activeModule,
    queryVisible,
    resultsVisible,
    detailVisible,
    isStationsModule,
    stationCount,
    recordCount,
    userCount,
    openQuery,
    openResults,
    openDetail,
    closeAll,
  }
})
