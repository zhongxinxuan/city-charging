import { loadDataset, type Dataset } from '../data/dataset'

export interface ChartPoint {
  name: string
  value: number
}

function groupBy(rows: { name: string }[]): ChartPoint[] {
  const m = new Map<string, number>()
  for (const r of rows) m.set(r.name, (m.get(r.name) ?? 0) + 1)
  return [...m.entries()]
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
}

async function getDataset(): Promise<Dataset> {
  return loadDataset()
}

export async function getStationsByCityChart(): Promise<ChartPoint[]> {
  const ds = await getDataset()
  const rows = ds.cities.map((c) => ({
    name: c.city_name,
    value: ds.stations.filter((s) => s.city_id === c.city_id).length,
  }))
  return rows.sort((a, b) => b.value - a.value)
}

export async function getOperatorShareChart(): Promise<ChartPoint[]> {
  const ds = await getDataset()
  const rows = ds.operators.map((o) => ({
    name: o.operator_name,
    value: ds.stations.filter((s) => s.operator_id === o.operator_id).length,
  }))
  return rows.sort((a, b) => b.value - a.value)
}

export async function getStationTypeDistributionChart(): Promise<ChartPoint[]> {
  const ds = await getDataset()
  const rows = ds.specs.map((sp) => ({
    name: sp.type_name,
    value: ds.stations.filter((s) => s.spec_id === sp.spec_id).length,
  }))
  return rows.sort((a, b) => b.value - a.value)
}

export async function getPaymentMethodDistributionChart(): Promise<ChartPoint[]> {
  const ds = await getDataset()
  return groupBy(
    ds.records.map((r) => ({ name: r.payment_method ?? '未知' })),
  )
}

export async function getRecordsByCityChart(): Promise<ChartPoint[]> {
  const ds = await getDataset()
  const rows = ds.cities.map((c) => {
    const stationIds = new Set(
      ds.stations.filter((s) => s.city_id === c.city_id).map((s) => s.station_id),
    )
    return {
      name: c.city_name,
      value: ds.records.filter((r) => stationIds.has(r.station_id)).length,
    }
  })
  return rows.sort((a, b) => b.value - a.value)
}

export async function getAvgCostByCityChart(): Promise<ChartPoint[]> {
  const ds = await getDataset()
  return ds.cities.map((c) => {
    const stationIds = new Set(
      ds.stations.filter((s) => s.city_id === c.city_id).map((s) => s.station_id),
    )
    const costs = ds.records
      .filter((r) => stationIds.has(r.station_id) && r.cost_yuan != null)
      .map((r) => r.cost_yuan!)
    const avg = costs.length
      ? Math.round((costs.reduce((a, b) => a + b, 0) / costs.length) * 100) / 100
      : 0
    return { name: c.city_name, value: avg }
  }).sort((a, b) => b.value - a.value)
}

export async function getAvgEnergyByCityChart(): Promise<ChartPoint[]> {
  const ds = await getDataset()
  return ds.cities.map((c) => {
    const stationIds = new Set(
      ds.stations.filter((s) => s.city_id === c.city_id).map((s) => s.station_id),
    )
    const energies = ds.records
      .filter((r) => stationIds.has(r.station_id) && r.energy_kwh != null)
      .map((r) => r.energy_kwh!)
    const avg = energies.length
      ? Math.round((energies.reduce((a, b) => a + b, 0) / energies.length) * 100) / 100
      : 0
    return { name: c.city_name, value: avg }
  }).sort((a, b) => b.value - a.value)
}
