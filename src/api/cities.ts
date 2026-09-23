import { http } from './http'

export interface City {
  city_id: number
  city_name: string
  longitude: number | null
  latitude: number | null
  area_code: string | null
  population: number | null
  gdp_billion: number | null
}

export async function getCities() {
  const response = await http.get<{ data: City[] }>('/api/cities')
  return response.data.data
}