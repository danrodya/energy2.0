import api from './api';

export const scheduleAPI = {
  getAll: (deviceId, status) => {
    const params = {};
    if (deviceId) params.device_id = deviceId;
    if (status) params.status = status;
    return api.get('/schedules/', { params });
  },

  getOne: (id) => api.get(`/schedules/${id}/`),
  create: (data) => api.post('/schedules/', data),
  update: (id, data) => api.put(`/schedules/${id}/`, data),
  delete: (id) => api.delete(`/schedules/${id}/`),

  activate: (id) => api.post(`/schedules/${id}/activate/`),
  deactivate: (id) => api.post(`/schedules/${id}/deactivate/`),
  toggleEnabled: (id) => api.patch(`/schedules/${id}/toggle_enabled/`),
  history: (id, days = 30) => api.get(`/schedules/${id}/history/`, { params: { days } }),

  getTemplates: (deviceType) => {
    const params = {};
    if (deviceType) params.device_type = deviceType;
    return api.get('/schedules/templates/', { params });
  },

  createFromTemplate: (templateId, deviceId) =>
    api.post('/schedules/from_template/', {
      template_id: templateId,
      device_id: deviceId,
    }),
};
