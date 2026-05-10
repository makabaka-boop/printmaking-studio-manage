import axios from 'axios'
import { message } from 'ant-design-vue'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    message.error(error.response?.data?.detail || '请求失败')
    return Promise.reject(error)
  }
)

export default request
