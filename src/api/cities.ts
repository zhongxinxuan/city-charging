import { loadDataset } from '../data/dataset'

export interface City {
  city_id: number
  city_name: string
  longitude: number | null
  latitude: number | null
  area_code: string | null
  population: number | null
  gdp_billion: number | null
}

export async function getCities(): Promise<City[]> {
  const ds = await loadDataset()
  return ds.cities
}
