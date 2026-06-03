import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Devices API
export const devicesAPI = {
  getAll: () => api.get('/devices/'),
  getOne: (id) => api.get(`/devices/${id}/`),
  toggle: (id) => api.post(`/devices/${id}/toggle/`),
  getSummary: () => api.get('/devices/summary/'),
  create: (data) => api.post('/devices/', data),
  update: (id, data) => api.put(`/devices/${id}/`, data),
  remove: (id) => api.delete(`/devices/${id}/`),
  getHistory: (id) => api.get(`/devices/${id}/history/`),
  getErrors: (id) => api.get(`/devices/${id}/errors/`),
};

// Energy API
export const energyAPI = {
  getCurrent: () => api.get('/energy/current/'),
  getToday: () => api.get('/energy/today/'),
  getHourly: (date) => api.get(`/energy/hourly/?date=${date}`),
  getDaily: (year, month) => api.get(`/energy/daily/?year=${year}&month=${month}`),
  getMonthly: (year) => api.get(`/energy/monthly/?year=${year}`),
  getStatistics: () => api.get('/energy/statistics/'),
  getTopConsumers: () => api.get('/energy/top_consumers/'),
  getForecast: () => api.get('/energy/forecast/'),
  getComparison: (period) => api.get(`/energy/comparison/?period=${period}`),
  getExportData: (format) => api.get(`/energy/export/?format=${format}`),
};


// Anomaly & Savings API
export const anomalyAPI = {
  getAnomalies: (resolved = false) => api.get(`/energy/anomalies/?resolved=${resolved}`),
  getAllAnomalies: () => api.get('/energy/anomalies/?resolved=true'),
  detectAnomalies: () => api.post('/energy/detect_anomalies/'),
  resolveAnomaly: (id) => api.post('/energy/resolve_anomaly/', { anomaly_id: id }),
  getScenarios: (implemented) => api.get(`/energy/saving_scenarios/${implemented ? '?implemented=true' : ''}`),
  generateScenarios: () => api.post('/energy/generate_scenarios/'),
};

export default api;
