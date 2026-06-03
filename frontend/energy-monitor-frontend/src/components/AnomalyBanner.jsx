import React, { useState, useEffect } from 'react';
import { anomalyAPI } from '../services/api';

const severityLabels = { high: 'Высокая', medium: 'Средняя', low: 'Низкая' };

function AnomalyBanner() {
  const [anomalies, setAnomalies] = useState([]);
  const [status, setStatus] = useState('check');

  const fetchAll = async () => {
    try {
      setStatus('check');
      await anomalyAPI.detectAnomalies();
      const res = await anomalyAPI.getAnomalies();
      setAnomalies(res.data);
      setStatus(res.data.length > 0 ? 'alert' : 'ok');
    } catch (err) {
      console.error('AnomalyBanner error:', err);
      setStatus('error');
    }
  };

  const handleResolve = async (id) => {
    try {
      await anomalyAPI.resolveAnomaly(id);
      setAnomalies(prev => prev.filter(a => a.id !== id));
    } catch (err) {
      console.error('Resolve error:', err);
    }
  };

  useEffect(() => {
    fetchAll();
    const i1 = setInterval(fetchAll, 60000);
    return () => clearInterval(i1);
  }, []);

  return (
    <div className="anomaly-banner">
      <div className='section-title'>
        {status === 'check' && 'Проверка аномалий...'}
        {status === 'ok' && 'Аномалий не обнаружено'}
        {status === 'alert' && `Аномалии: ${anomalies.length}`}
        {status === 'error' && 'Ошибка соединения с сервером'}
      </div>
      <div className='anomaly-list'>
        {status === 'alert' && anomalies.map(a => (
          <div className="anomaly-card" key={a.id}>
            <div className='anomaly-item'>
              <div className='anomaly-item-title'>{a.device_name}</div>
              <div className='anomaly-item-content'>{a.description}</div>
              <div className='anomaly-item-context'>
                {severityLabels[a.severity]}
                {a.ml_score ? ` | ML: ${(a.ml_score * 100).toFixed(0)}%` : ''}
                {a.current_value ? ` | тек.: ${a.current_value.toFixed(2)}` : ''}
              </div>
            </div>
            <button
              className='anomaly-item-button'
              onClick={() => handleResolve(a.id)}
            >
              Прочитано
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default AnomalyBanner;
