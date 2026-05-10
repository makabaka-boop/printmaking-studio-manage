import request from './request'

export const artworksApi = {
  list: () => request.get('/artworks'),
  get: (id) => request.get(`/artworks/${id}`),
  create: (data) => request.post('/artworks', data),
  update: (id, data) => request.put(`/artworks/${id}`, data),
  delete: (id) => request.delete(`/artworks/${id}`),
  export: (id) => window.open(`/api/export/artwork/${id}`)
}

export const platesApi = {
  list: (artworkId) => request.get('/plates', { params: { artwork_id: artworkId } }),
  get: (id) => request.get(`/plates/${id}`),
  create: (data) => request.post('/plates', data),
  update: (id, data) => request.put(`/plates/${id}`, data),
  delete: (id) => request.delete(`/plates/${id}`)
}

export const papersApi = {
  list: (lowStock = false) => request.get('/papers', { params: { low_stock: lowStock } }),
  get: (id) => request.get(`/papers/${id}`),
  create: (data) => request.post('/papers', data),
  update: (id, data) => request.put(`/papers/${id}`, data),
  delete: (id) => request.delete(`/papers/${id}`)
}

export const batchesApi = {
  list: () => request.get('/batches'),
  get: (id) => request.get(`/batches/${id}`),
  create: (data) => request.post('/batches', data),
  update: (id, data) => request.put(`/batches/${id}`, data),
  delete: (id) => request.delete(`/batches/${id}`)
}

export const dashboardApi = {
  stats: () => request.get('/dashboard/stats'),
  printTypeChart: () => request.get('/dashboard/print-type-chart'),
  recentBatchesChart: () => request.get('/dashboard/recent-batches-chart'),
  wasteRateChart: () => request.get('/dashboard/waste-rate-chart'),
  lowStockPapers: () => request.get('/dashboard/low-stock-papers')
}
