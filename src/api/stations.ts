import { http } from './http'

export interface StationQuery {
  city_id?: number
  operator_id?: number
  keyword?: string
}

export interface StationListItem {
  station_id: number
  station_name: string
  city_name: string
  operator_name: string
  type_name: string
  power_kw: number | null
}

export interface StationDetail {
  station_id: number
  station_name: string
  address: string | null
  phone: string | null
  longitude: number | null
  latitude: number | null
  city_name: string
  operator_name: string
  type_name: string
  power_kw: number | null
  voltage_v: number | null
  current_a: number | null
  connector_type: string | null
  charge_time_min: number | null
  cost_per_kwh: number | null
  opening_hours: string | null
  has_restroom: boolean | null
  parking_spots: number | null
}

export async function getStations(query: StationQuery = {}) {
  const response = await http.get<{ data: StationListItem[] }>('/api/stations', {
    params: query,
  })

  return response.data.data
}

export async function getStationDetail(stationId: number) {
  const response = await http.get<{ data: StationDetail }>(`/api/stations/${stationId}`)
  return response.data.data
}