import { http } from './http'

export interface RecordQuery {
  city_id?: number
  payment_method?: string
  keyword?: string
}

export interface RecordListItem {
  record_id: string
  username: string
  station_name: string
  city_name: string
  charge_start_time: string | null
  duration_minutes: number | null
  energy_kwh: number | null
  cost_yuan: number | null
  payment_method: string | null
}

export interface RecordDetail {
  record_id: string
  user_id: string
  username: string
  phone: string | null
  user_type: string | null
  vehicle_type: string | null
  vehicle_model: string | null
  station_id: number
  station_name: string
  city_name: string
  charge_start_time: string | null
  charge_end_time: string | null
  duration_minutes: number | null
  energy_kwh: number | null
  cost_yuan: number | null
  payment_method: string | null
  start_soc: number | null
  end_soc: number | null
}

export async function getRecords(query: RecordQuery = {}) {
  const response = await http.get<{ data: RecordListItem[] }>('/api/records', {
    params: query,
  })

  return response.data.data
}

export async function getRecordDetail(recordId: string) {
  const response = await http.get<{ data: RecordDetail }>(`/api/records/${recordId}`)
  return response.data.data
}
