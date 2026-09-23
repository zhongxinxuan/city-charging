import { loadDataset, type Dataset } from '../data/dataset'

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

function stationCityId(ds: Dataset, stationId: number): number {
  return ds.stations.find((s) => s.station_id === stationId)?.city_id ?? -1
}
function stationName(ds: Dataset, stationId: number): string {
  return ds.stations.find((s) => s.station_id === stationId)?.station_name ?? ''
}
function cityName(ds: Dataset, id: number): string {
  return ds.cities.find((c) => c.city_id === id)?.city_name ?? ''
}

export async function getRecords(query: RecordQuery = {}): Promise<RecordListItem[]> {
  const ds = await loadDataset()
  let rows = ds.records
  if (query.city_id != null) {
    rows = rows.filter((r) => stationCityId(ds, r.station_id) === query.city_id)
  }
  if (query.payment_method) {
    rows = rows.filter((r) => r.payment_method === query.payment_method)
  }
  if (query.keyword) {
    const kw = query.keyword.toLowerCase()
    rows = rows.filter((r) => {
      const u = ds.users.find((x) => x.user_id === r.user_id)
      return (
        r.record_id.toLowerCase().includes(kw) ||
        (u?.username ?? '').toLowerCase().includes(kw) ||
        stationName(ds, r.station_id).toLowerCase().includes(kw)
      )
    })
  }
  // 按开始时间倒序
  rows = [...rows].sort((a, b) =>
    (b.charge_start_time ?? '').localeCompare(a.charge_start_time ?? ''),
  )
  return rows.slice(0, 50).map((r) => {
    const u = ds.users.find((x) => x.user_id === r.user_id)
    const sid = r.station_id
    return {
      record_id: r.record_id,
      username: u?.username ?? '',
      station_name: stationName(ds, sid),
      city_name: cityName(ds, stationCityId(ds, sid)),
      charge_start_time: r.charge_start_time,
      duration_minutes: r.duration_minutes,
      energy_kwh: r.energy_kwh,
      cost_yuan: r.cost_yuan,
      payment_method: r.payment_method,
    }
  })
}

export async function getRecordDetail(recordId: string): Promise<RecordDetail> {
  const ds = await loadDataset()
  const r = ds.records.find((x) => x.record_id === recordId)
  if (!r) throw new Error('充电记录不存在')
  const u = ds.users.find((x) => x.user_id === r.user_id)!
  const sid = r.station_id
  const cityId = stationCityId(ds, sid)
  return {
    record_id: r.record_id,
    user_id: r.user_id,
    username: u.username,
    phone: u.phone,
    user_type: u.user_type,
    vehicle_type: u.vehicle_type,
    vehicle_model: u.vehicle_model,
    station_id: sid,
    station_name: stationName(ds, sid),
    city_name: cityName(ds, cityId),
    charge_start_time: r.charge_start_time,
    charge_end_time: r.charge_end_time,
    duration_minutes: r.duration_minutes,
    energy_kwh: r.energy_kwh,
    cost_yuan: r.cost_yuan,
    payment_method: r.payment_method,
    start_soc: r.start_soc,
    end_soc: r.end_soc,
  }
}
