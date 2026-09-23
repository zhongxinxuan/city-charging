import { http } from './http'

export interface ChartPoint {
  name: string
  value: number
}

export async function getStationsByCityChart() {
  const response = await http.get<{ data: ChartPoint[] }>('/api/charts/stations-by-city')
  return response.data.data
}

export async function getOperatorShareChart() {
  const response = await http.get<{ data: ChartPoint[] }>('/api/charts/operator-share')
  return response.data.data
}

export async function getStationTypeDistributionChart() {
  const response = await http.get<{ data: ChartPoint[] }>('/api/charts/station-type-distribution')
  return response.data.data
}

export async function getPaymentMethodDistributionChart() {
  const response = await http.get<{ data: ChartPoint[] }>('/api/charts/payment-method-distribution')
  return response.data.data
}

export async function getRecordsByCityChart() {
  const response = await http.get<{ data: ChartPoint[] }>('/api/charts/records-by-city')
  return response.data.data
}

export async function getAvgCostByCityChart() {
  const response = await http.get<{ data: ChartPoint[] }>('/api/charts/avg-cost-by-city')
  return response.data.data
}

export async function getAvgEnergyByCityChart() {
  const response = await http.get<{ data: ChartPoint[] }>('/api/charts/avg-energy-by-city')
  return response.data.data
}
