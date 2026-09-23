import { loadDataset, type Dataset } from '../data/dataset'

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

function cityName(ds: Dataset, id: number): string {
  return ds.cities.find((c) => c.city_id === id)?.city_name ?? ''
}
function operatorName(ds: Dataset, id: number): string {
  return ds.operators.find((o) => o.operator_id === id)?.operator_name ?? ''
}
function specOf(ds: Dataset, id: number) {
  return ds.specs.find((s) => s.spec_id === id)
}

export async function getStations(query: StationQuery = {}): Promise<StationListItem[]> {
  const ds = await loadDataset()
  let rows = ds.stations
  if (query.city_id != null) rows = rows.filter((r) => r.city_id === query.city_id)
  if (query.operator_id != null) rows = rows.filter((r) => r.operator_id === query.operator_id)
  if (query.keyword) {
    const kw = query.keyword.toLowerCase()
    rows = rows.filter(
      (r) =>
        r.station_name.toLowerCase().includes(kw) ||
        (r.address ?? '').toLowerCase().includes(kw),
    )
  }
  return rows.slice(0, 50).map((r) => {
    const sp = specOf(ds, r.spec_id)
    return {
      station_id: r.station_id,
      station_name: r.station_name,
      city_name: cityName(ds, r.city_id),
      operator_name: operatorName(ds, r.operator_id),
      type_name: sp?.type_name ?? '',
      power_kw: sp?.power_kw ?? null,
    }
  })
}

export async function getStationDetail(stationId: number): Promise<StationDetail> {
  const ds = await loadDataset()
  const r = ds.stations.find((s) => s.station_id === stationId)
  if (!r) throw new Error('充电站不存在')
  const sp = specOf(ds, r.spec_id)!
  return {
    station_id: r.station_id,
    station_name: r.station_name,
    address: r.address,
    phone: r.phone,
    longitude: r.longitude,
    latitude: r.latitude,
    city_name: cityName(ds, r.city_id),
    operator_name: operatorName(ds, r.operator_id),
    type_name: sp.type_name,
    power_kw: sp.power_kw,
    voltage_v: sp.voltage_v,
    current_a: sp.current_a,
    connector_type: sp.connector_type,
    charge_time_min: sp.charge_time_min,
    cost_per_kwh: sp.cost_per_kwh,
    opening_hours: r.opening_hours,
    has_restroom: r.has_restroom,
    parking_spots: r.parking_spots,
  }
}
