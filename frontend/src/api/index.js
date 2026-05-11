import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8031'
})

export default {
  getArtworks: () => api.get('/artworks/'),
  createArtwork: (data) => api.post('/artworks/', data),
  deleteArtwork: (id) => api.delete(`/artworks/${id}`),
  
  getPlates: () => api.get('/plates/'),
  getPlatesByArtwork: (artworkId) => api.get(`/plates/artwork/${artworkId}`),
  createPlate: (data) => api.post('/plates/', data),
  updatePlate: (id, data) => api.put(`/plates/${id}`, data),
  deletePlate: (id) => api.delete(`/plates/${id}`),
  
  getPapers: () => api.get('/papers/'),
  getLowStockPapers: () => api.get('/papers/low-stock/'),
  createPaper: (data) => api.post('/papers/', data),
  updatePaper: (id, data) => api.put(`/papers/${id}`, data),
  deletePaper: (id) => api.delete(`/papers/${id}`),
  
  getBatches: () => api.get('/batches/'),
  getBatchesByArtwork: (artworkId) => api.get(`/batches/artwork/${artworkId}`),
  createBatch: (data) => api.post('/batches/', data),
  deleteBatch: (id) => api.delete(`/batches/${id}`),
  
  getDashboardStats: () => api.get('/dashboard/stats'),
  getPrintTypes: () => api.get('/dashboard/print-types'),
  getMonthlyBatches: () => api.get('/dashboard/monthly-batches'),
  getWasteRates: () => api.get('/dashboard/waste-rates'),
  
  exportEdition: (artworkId) => {
    window.open(`http://localhost:8031/export/edition/${artworkId}`, '_blank')
  }
}
