import { http } from './http'

export interface Operator {
  operator_id: number
  operator_name: string
  company_type: string | null
  founded_year: number | null
  headquarters: string | null
}

export async function getOperators() {
  const response = await http.get<{ data: Operator[] }>('/api/operators')
  return response.data.data
}
