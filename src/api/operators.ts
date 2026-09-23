import { loadDataset } from '../data/dataset'

export interface Operator {
  operator_id: number
  operator_name: string
  company_type: string | null
  founded_year: number | null
  headquarters: string | null
}

export async function getOperators(): Promise<Operator[]> {
  const ds = await loadDataset()
  return ds.operators
}
