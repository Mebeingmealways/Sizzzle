const API_BASE = import.meta.env.VITE_API_BASE || '/api'

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('sizzzle_token')
  const headers = {
    'Content-Type': 'application/json',
    ...(token && token !== 'undefined' && token !== 'null' && { Authorization: `Bearer ${token}` }),
    ...options.headers
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  })

  let data
  const text = await response.text()
  try {
    data = text ? JSON.parse(text) : {}
  } catch {
    throw new Error('Server returned an invalid response')
  }

  if (response.status === 401) {
    localStorage.removeItem('sizzzle_token')
    localStorage.removeItem('sizzzle_user')
    throw new Error(data.error || data.message || 'Unauthorized')
  }

  if (!response.ok) {
    throw new Error(data.error || data.message || 'Request failed')
  }

  return data
}

export const api = {
  get: (url) => request(url),
  post: (url, body = {}) => request(url, { method: 'POST', body: JSON.stringify(body) }),
  put: (url, body = {}) => request(url, { method: 'PUT', body: JSON.stringify(body) }),
  patch: (url, body = {}) => request(url, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: (url) => request(url, { method: 'DELETE' })
}

// Auth
export const authApi = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (data) => api.post('/auth/register', data),
  registerCook: (data) => api.post('/auth/register/cook', data),
  verifyEmail: (data) => api.post('/auth/verify-email', data),
  resendOtp: (data) => api.post('/auth/resend-otp', data),
  forgotPassword: (data) => api.post('/auth/forgot-password', data),
  resetPassword: (data) => api.post('/auth/reset-password', data),
  me: () => api.get('/auth/me'),
  changePassword: (data) => api.post('/auth/change-password', data)
}

// Bookings
export const bookingApi = {
  create: (data) => api.post('/bookings', data),
  list: (params = '') => api.get(`/bookings${params ? '?' + params : ''}`),
  get: (id) => api.get(`/bookings/${id}`),
  cancel: (id) => api.post(`/bookings/${id}/cancel`),
  updateStatus: (id, status) => api.patch(`/bookings/${id}/status`, { status }),
  verifyOtp: (id, otp) => api.post(`/bookings/${id}/verify-otp`, { otp }),
  startService: (id) => api.post(`/bookings/${id}/start`),
  endService: (id) => api.post(`/bookings/${id}/end`),
  rate: (id, data) => api.post(`/bookings/${id}/rate`, data),
  getCookLocation: (id) => api.get(`/bookings/${id}/cook-location`)
}

// Cooks
export const cookApi = {
  list: (params = '') => api.get(`/cooks${params ? '?' + params : ''}`),
  get: (id) => api.get(`/cooks/${id}`),
  recommend: (params) => api.post('/cooks/recommend', params),
  updateAvailability: (data) => api.put('/cooks/availability', data),
  updateLocation: (data) => api.post('/cooks/location', data),
  getEarnings: (params = '') => api.get(`/cooks/earnings${params ? '?' + params : ''}`),
  getJobs: (params = '') => api.get(`/cooks/jobs${params ? '?' + params : ''}`)
}

// Dishes
export const dishApi = {
  list: (params = '') => api.get(`/dishes${params ? '?' + params : ''}`),
  get: (id) => api.get(`/dishes/${id}`),
  getIngredients: (dishIds) => api.post('/dishes/ingredients', { dish_ids: dishIds })
}

// Manager
export const managerApi = {
  getVerifications: (status = 'pending') => api.get(`/manager/verification-queue?status=${status}`),
  getPendingVerifications: () => api.get('/manager/verifications/pending'),
  getVerificationDetail: (id) => api.get(`/manager/verifications/${id}`),
  verifyAction: (id, action) => api.post(`/manager/verifications/${id}`, action),
  setCookStatus: (id, data) => api.patch(`/manager/cooks/${id}/status`, data),
  getComplaints: () => api.get('/manager/complaints'),
  createComplaint: (data) => api.post('/manager/complaints', data),
  resolveComplaint: (id, data) => api.post(`/manager/complaints/${id}/resolve`, data),
  updateComplaint: (id, data) => api.patch(`/manager/complaints/${id}`, data),
  getCookMetrics: () => api.get('/manager/cook-metrics'),
  getCooks: () => api.get('/manager/cooks')
}

// Admin
export const adminApi = {
  getStats: () => api.get('/admin/stats'),
  getAnalytics: (period = '30d') => api.get(`/admin/analytics?period=${period}`),
  getManagers: () => api.get('/admin/managers'),
  createManager: (data) => api.post('/admin/managers', data),
  assignRegion: (id, data) => api.post(`/admin/managers/${id}/region`, data),
  getPolicies: () => api.get('/admin/policies'),
  updatePolicies: (policies) => api.put('/admin/policies', { policies }),
  updatePolicy: (id, data) => api.put(`/admin/policies/${id}`, data),
  getDisputes: () => api.get('/admin/disputes'),
  resolveDispute: (id, data) => api.post(`/admin/disputes/${id}/resolve`, data)
}

// User profile
export const profileApi = {
  get: () => api.get('/profile'),
  update: (data) => api.put('/profile', data),
  updateTasteProfile: (data) => api.put('/profile/taste', data),
  getTasteProfile: () => api.get('/profile/taste'),
  getKitchenChecklist: () => api.get('/profile/kitchen-checklist'),
  updateKitchenChecklist: (data) => api.put('/profile/kitchen-checklist', data)
}

// Notifications
export const notificationApi = {
  list: (limit = 20, unreadOnly = false) => api.get(`/notifications?limit=${limit}&unread_only=${unreadOnly}`),
  unreadCount: () => api.get('/notifications/unread-count'),
  markRead: (id) => api.post(`/notifications/${id}/read`),
  markAllRead: () => api.post('/notifications/read-all')
}
