/**
 * 纯静态数据层：启动时一次性加载 public/data_json/*.json，
 * 之后所有查询都在浏览器内存里完成，不再需要后端 API。
 */

export interface CityRow {
  city_id: number
  city_name: string
  longitude: number | null
  latitude: number | null
  area_code: string | null
  population: number | null
  gdp_billion: number | null
}

export interface OperatorRow {
  operator_id: number
  operator_name: string
  company_type: string | null
  founded_year: number | null
  headquarters: string | null
}

export interface SpecRow {
  spec_id: number
  type_name: string
  power_kw: number | null
  voltage_v: number | null
  current_a: number | null
  connector_type: string | null
  charge_time_min: number | null
  cost_per_kwh: number | null
}

export interface StationRow {
  station_id: number
  station_name: string
  address: string | null
  phone: string | null
  longitude: number | null
  latitude: number | null
  city_id: number
  operator_id: number
  spec_id: number
  opening_hours: string | null
  has_restroom: boolean | null
  parking_spots: number | null
}

export interface UserRow {
  user_id: string
  username: string
  phone: string | null
  user_type: string | null
  vehicle_type: string | null
  vehicle_model: string | null
  registration_date: string | null
  total_charge_count: number | null
  total_charge_kwh: number | null
  preferred_city_id: number | null
}

export interface RecordRow {
  record_id: string
  user_id: string
  station_id: number
  charge_start_time: string | null
  charge_end_time: string | null
  duration_minutes: number | null
  energy_kwh: number | null
  cost_yuan: number | null
  payment_method: string | null
  start_soc: number | null
  end_soc: number | null
}

export interface Dataset {
  cities: CityRow[]
  operators: OperatorRow[]
  specs: SpecRow[]
  stations: StationRow[]
  users: UserRow[]
  records: RecordRow[]
}

function toNum(v: unknown): number | null {
  if (v === null || v === undefined || v === '') return null
  const n = Number(v)
  return isNaN(n) ? null : n
}

function toBool(v: unknown): boolean | null {
  if (v === null || v === undefined || v === '') return null
  return String(v).toUpperCase() === 'TRUE' || v === 1
}

function str(v: unknown): string | null {
  if (v === null || v === undefined || v === '') return null
  return String(v)
}

let cache: Promise<Dataset> | null = null

export function loadDataset(): Promise<Dataset> {
  if (cache) return cache
  cache = (async () => {
    const [citiesRaw, operatorsRaw, specsRaw, stationsRaw, usersRaw, recordsRaw] =
      await Promise.all([
        fetch('/data_json/expanded_cities.json').then((r) => r.json()),
        fetch('/data_json/operators_info.json').then((r) => r.json()),
        fetch('/data_json/charger_specifications.json').then((r) => r.json()),
        fetch('/data_json/expanded_stations.json').then((r) => r.json()),
        fetch('/data_json/users.json').then((r) => r.json()),
        fetch('/data_json/charging_records.json').then((r) => r.json()),
      ])

    const cities: CityRow[] = citiesRaw.map((r: any) => ({
      city_id: toNum(r.city_id)!,
      city_name: r.city_name,
      longitude: toNum(r.longitude),
      latitude: toNum(r.latitude),
      area_code: str(r.area_code),
      population: toNum(r.population),
      gdp_billion: toNum(r.gdp_billion),
    }))

    const operators: OperatorRow[] = operatorsRaw.map((r: any) => ({
      operator_id: toNum(r.operator_id)!,
      operator_name: r.operator_name,
      company_type: str(r.company_type),
      founded_year: toNum(r.founded_year),
      headquarters: str(r.headquarters),
    }))

    const specs: SpecRow[] = specsRaw.map((r: any) => ({
      spec_id: toNum(r.spec_id)!,
      type_name: r.type_name,
      power_kw: toNum(r.power_kw),
      voltage_v: toNum(r.voltage_v),
      current_a: toNum(r.current_a),
      connector_type: str(r.connector_type),
      charge_time_min: toNum(r.charge_time_min),
      cost_per_kwh: toNum(r.cost_per_kwh),
    }))

    const stations: StationRow[] = stationsRaw.map((r: any) => ({
      station_id: toNum(r.station_id)!,
      station_name: r.station_name,
      address: str(r.address),
      phone: str(r.phone),
      longitude: toNum(r.longitude),
      latitude: toNum(r.latitude),
      city_id: toNum(r.city_id)!,
      operator_id: toNum(r.operator_id)!,
      spec_id: toNum(r.spec_id)!,
      opening_hours: str(r.opening_hours),
      has_restroom: toBool(r.has_restroom),
      parking_spots: toNum(r.parking_spots),
    }))

    const users: UserRow[] = usersRaw.map((r: any) => ({
      user_id: r.user_id,
      username: r.username,
      phone: str(r.phone),
      user_type: str(r.user_type),
      vehicle_type: str(r.vehicle_type),
      vehicle_model: str(r.vehicle_model),
      registration_date: str(r.registration_date),
      total_charge_count: toNum(r.total_charge_count),
      total_charge_kwh: toNum(r.total_charge_kwh),
      preferred_city_id: toNum(r.preferred_city_id),
    }))

    const records: RecordRow[] = recordsRaw.map((r: any) => ({
      record_id: r.record_id,
      user_id: r.user_id,
      station_id: toNum(r.station_id)!,
      charge_start_time: str(r.charge_start_time),
      charge_end_time: str(r.charge_end_time),
      duration_minutes: toNum(r.duration_minutes),
      energy_kwh: toNum(r.energy_kwh),
      cost_yuan: toNum(r.cost_yuan),
      payment_method: str(r.payment_method),
      start_soc: toNum(r.start_soc),
      end_soc: toNum(r.end_soc),
    }))

    return { cities, operators, specs, stations, users, records }
  })()
  return cache
}
