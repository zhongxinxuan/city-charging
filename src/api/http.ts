import axios from 'axios'

export const http = axios.create({
  // 线上部署时前端与后端同源（FastAPI 同时托管 dist/），无需指定域名。
  // 本地开发时由 vite.config.ts 的 proxy 把 /api 转发到 127.0.0.1:8000。
  baseURL: '',
  timeout: 15000,
})
