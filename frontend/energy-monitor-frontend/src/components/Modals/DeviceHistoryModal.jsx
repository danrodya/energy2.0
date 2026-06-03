import React, { useState, useEffect } from 'react';
import { devicesAPI } from '../../services/api';
import { formatDateTime } from '../../utils/dateUtils';

function DeviceHistoryModal({ deviceId, deviceName, onClose }) {
  const [history, setHistory] = useState([]);
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('history');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [historyRes, errorsRes] = await Promise.all([
          devicesAPI.getHistory(deviceId),
          devicesAPI.getErrors(deviceId),
        ]);
        setHistory(historyRes.data || []);
        setErrors(errorsRes.data || []);
      } catch (error) {
        console.error('Ошибка загрузки:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [deviceId]);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{deviceName} - История</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-tabs">
          <button
            className={`tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            🕐 История действий
          </button>
          <button
            className={`tab ${activeTab === 'errors' ? 'active' : ''}`}
            onClick={() => setActiveTab('errors')}
          >
            ⚠️ Ошибки и требования
          </button>
        </div>

        <div className="modal-body">
          {loading ? (
            <div className="loading">Загрузка...</div>
          ) : activeTab === 'history' ? (
            <div className="history-list">
              {history.length > 0 ? (
                history.map((item, idx) => (
                  <div key={idx} className="history-item">
                    <div className="history-time">{formatDateTime(item.timestamp)}</div>
                    <div className="history-action">{item.action}</div>
                    <div className="history-details">{item.details}</div>
                  </div>
                ))
              ) : (
                <p>Нет истории</p>
              )}
            </div>
          ) : (
            <div className="errors-list">
              {errors.length > 0 ? (
                errors.map((error, idx) => (
                  <div key={idx} className={`error-item severity-${error.severity}`}>
                    <div className="error-title">{error.title}</div>
                    <div className="error-description">{error.description}</div>
                    <div className="error-date">{formatDateTime(error.date)}</div>
                  </div>
                ))
              ) : (
                <p>Нет ошибок</p>
              )}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>Закрыть</button>
        </div>
      </div>
    </div>
  );
}

export default DeviceHistoryModal;
