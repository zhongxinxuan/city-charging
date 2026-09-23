import { http } from './http'

export interface ChargerSpec {
  spec_id: number
  type_name: string
  power_kw: number | null
  voltage_v: number | null
  current_a: number | null
  connector_type: string | null
  charge_time_min: number | null
  cost_per_kwh: number | null
}

export async function getChargerSpecs() {
  const response = await http.get<{ data: ChargerSpec[] }>('/api/charger-specs')
  return response.data.data
}
